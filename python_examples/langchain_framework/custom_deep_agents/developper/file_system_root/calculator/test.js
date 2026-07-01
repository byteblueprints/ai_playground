function testCalculator() {
    let errors = 0;

    function click(action) {
        document.querySelector(`[data-action='${action}']`).click();
    }

    function expect(value, message) {
        const actual = document.getElementById('display').textContent;
        if (actual !== value) {
            console.error(`${message} — expected '${value}', got '${actual}'`);
            errors++;
        }
    }

    function reset() {
        click('clear');
    }

    reset();
    click('7'); click('plus'); click('5'); click('equals');
    expect('12', 'addition');

    click('equals');
    expect('17', 'repeated equals should reuse last operand');

    reset();
    click('1'); click('0'); click('minus'); click('3'); click('equals');
    expect('7', 'subtraction');

    reset();
    click('8'); click('divide'); click('2'); click('equals');
    expect('4', 'division');

    reset();
    click('4'); click('multiply'); click('3'); click('equals');
    expect('12', 'multiplication');

    reset();
    click('2'); click('dot'); click('5'); click('plus'); click('1'); click('dot'); click('2'); click('equals');
    expect('3.7', 'decimal arithmetic');

    reset();
    click('7'); click('divide'); click('0'); click('equals');
    expect('Error', 'division by zero');

    reset();
    click('5'); click('0'); click('percent');
    expect('0.5', 'percent conversion');

    reset();
    click('6'); click('plus-minus');
    expect('-6', 'sign toggle');

    reset();
    click('0'); click('0'); click('0');
    expect('0', 'leading zero handling');

    reset();
    click('9'); click('plus'); click('multiply'); click('3'); click('equals');
    expect('27', 'operator replacement before second operand');

    reset();
    click('5'); click('plus'); click('equals');
    expect('10', 'equals after operator should reuse first operand');

    if (errors === 0) {
        console.log('All tests passed!');
    } else {
        console.error(`${errors} test(s) failed.`);
    }

    return errors;
}

window.testCalculator = testCalculator;
