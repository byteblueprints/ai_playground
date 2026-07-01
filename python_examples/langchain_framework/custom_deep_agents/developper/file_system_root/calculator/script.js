const display = document.getElementById('display');
const buttons = document.querySelector('.buttons');
const operatorButtons = [...document.querySelectorAll('.operator:not(.equals)')];
const clearButton = document.querySelector('[data-action="clear"]');

const MAX_DISPLAY_LENGTH = 10;

const state = {
    displayValue: '0',
    firstOperand: null,
    operator: null,
    waitingForSecondOperand: false,
    lastOperand: null,
    justEvaluated: false,
    error: false
};

function formatNumber(value) {
    if (!Number.isFinite(value)) return 'Error';
    if (Object.is(value, -0)) value = 0;

    const absValue = Math.abs(value);

    if (absValue >= 1e10 || (absValue > 0 && absValue < 1e-9)) {
        return value.toExponential(4)
            .replace(/\.0+e/, 'e')
            .replace(/(\.\d*?)0+e/, '$1e')
            .replace('e+', 'e');
    }

    let text = value.toString();
    if (text.includes('e')) {
        return text.replace('e+', 'e');
    }

    if (text.includes('.')) {
        text = parseFloat(text).toString();
    }

    if (text.length > MAX_DISPLAY_LENGTH) {
        text = value.toPrecision(MAX_DISPLAY_LENGTH).replace(/\.0+$/, '');
        if (text.includes('e')) {
            text = text.replace('e+', 'e');
        } else {
            text = parseFloat(text).toString();
        }
    }

    return text;
}

function updateDisplay() {
    display.textContent = state.displayValue;
}

function setActiveOperator(action = null) {
    operatorButtons.forEach((button) => {
        button.classList.toggle('active', button.dataset.action === action);
    });
}

function resetState() {
    state.displayValue = '0';
    state.firstOperand = null;
    state.operator = null;
    state.waitingForSecondOperand = false;
    state.lastOperand = null;
    state.justEvaluated = false;
    state.error = false;
    clearButton.textContent = 'AC';
    setActiveOperator();
    updateDisplay();
}

function setDisplayValue(value) {
    state.displayValue = value;
    state.error = value === 'Error';
    clearButton.textContent = value === '0' && !state.firstOperand && !state.operator ? 'AC' : 'C';
    updateDisplay();
}

function performCalculation(operator, first, second) {
    switch (operator) {
        case 'plus':
            return first + second;
        case 'minus':
            return first - second;
        case 'multiply':
            return first * second;
        case 'divide':
            return second === 0 ? NaN : first / second;
        default:
            return second;
    }
}

function inputNumber(num) {
    if (state.error) resetState();

    if (state.justEvaluated && !state.operator) {
        state.firstOperand = null;
        state.lastOperand = null;
        state.justEvaluated = false;
        setActiveOperator();
    }

    if (state.waitingForSecondOperand) {
        state.displayValue = num;
        state.waitingForSecondOperand = false;
    } else if (state.displayValue === '0') {
        state.displayValue = num;
    } else if (state.displayValue.replace('-', '').replace('.', '').length < 15) {
        state.displayValue += num;
    }

    clearButton.textContent = 'C';
    updateDisplay();
}

function inputDot() {
    if (state.error) resetState();

    if (state.justEvaluated && !state.operator) {
        state.firstOperand = null;
        state.lastOperand = null;
        state.displayValue = '0';
        state.justEvaluated = false;
        setActiveOperator();
    }

    if (state.waitingForSecondOperand) {
        state.displayValue = '0.';
        state.waitingForSecondOperand = false;
        clearButton.textContent = 'C';
        updateDisplay();
        return;
    }

    if (!state.displayValue.includes('.')) {
        state.displayValue += '.';
        clearButton.textContent = 'C';
        updateDisplay();
    }
}

function inputOperator(nextOperator) {
    if (state.error) return;

    const inputValue = parseFloat(state.displayValue);

    if (state.operator && !state.waitingForSecondOperand) {
        const result = performCalculation(state.operator, state.firstOperand, inputValue);
        if (!Number.isFinite(result)) {
            setDisplayValue('Error');
            state.firstOperand = null;
            state.operator = null;
            state.waitingForSecondOperand = false;
            state.lastOperand = null;
            state.justEvaluated = true;
            setActiveOperator();
            return;
        }
        state.firstOperand = result;
        setDisplayValue(formatNumber(result));
    } else if (state.firstOperand === null) {
        state.firstOperand = inputValue;
    }

    state.operator = nextOperator;
    state.waitingForSecondOperand = true;
    state.justEvaluated = false;
    setActiveOperator(nextOperator);
}

function equals() {
    if (state.error || state.operator === null || state.firstOperand === null) return;

    let secondOperand;
    if (state.waitingForSecondOperand) {
        secondOperand = state.lastOperand ?? state.firstOperand;
    } else {
        secondOperand = parseFloat(state.displayValue);
        state.lastOperand = secondOperand;
    }

    const result = performCalculation(state.operator, state.firstOperand, secondOperand);

    if (!Number.isFinite(result)) {
        setDisplayValue('Error');
        state.firstOperand = null;
        state.operator = null;
        state.waitingForSecondOperand = false;
        state.lastOperand = null;
        state.justEvaluated = true;
        setActiveOperator();
        return;
    }

    state.firstOperand = result;
    state.displayValue = formatNumber(result);
    state.waitingForSecondOperand = true;
    state.justEvaluated = true;
    setActiveOperator();
    clearButton.textContent = 'C';
    updateDisplay();
}

function inputPercent() {
    if (state.error) return;
    const current = parseFloat(state.displayValue);
    const result = current / 100;
    setDisplayValue(formatNumber(result));

    if (!state.waitingForSecondOperand) {
        state.justEvaluated = false;
    }
}

function inputPlusMinus() {
    if (state.error) return;
    if (state.displayValue === '0') return;
    const current = parseFloat(state.displayValue);
    setDisplayValue(formatNumber(current * -1));
}

buttons.addEventListener('click', (event) => {
    const target = event.target.closest('.btn');
    if (!target) return;

    const action = target.dataset.action;

    if (target.classList.contains('number')) {
        if (action === 'dot') {
            inputDot();
        } else {
            inputNumber(action);
        }
        return;
    }

    if (target.classList.contains('operator')) {
        if (action === 'equals') {
            equals();
        } else {
            inputOperator(action);
        }
        return;
    }

    if (target.classList.contains('function')) {
        if (action === 'clear') resetState();
        if (action === 'percent') inputPercent();
        if (action === 'plus-minus') inputPlusMinus();
    }
});

resetState();