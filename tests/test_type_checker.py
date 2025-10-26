"""
Unit tests for the SPL type checker.
Tests semantic attribution rules from SPL_Types.pdf
"""

import pytest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from spl.parser import Parser
from spl.type_checker import TypeChecker


def parse_and_check(source: str) -> tuple[bool, list]:
    """Helper: parse and type check, return (is_correct, errors)"""
    parser = Parser(source)
    ast = parser.parse()
    checker = TypeChecker()
    is_correct = checker.check_program(ast)
    return is_correct, checker.get_errors()


class TestBasicTypes:
    """Test basic type checking rules"""
    
    def test_simple_numeric_assignment(self):
        """Variables are numeric, numbers are numeric"""
        source = """
        glob { x }
        proc { }
        func { }
        main {
          var { }
          x = 42
        }
        """
        is_correct, errors = parse_and_check(source)
        assert is_correct, f"Should pass but got errors: {errors}"
    
    def test_arithmetic_operations(self):
        """Arithmetic operators require numeric operands"""
        source = """
        glob { x y z }
        proc { }
        func { }
        main {
          var { }
          x = 10;
          y = 20;
          z = ( x plus y );
          z = ( x minus y );
          z = ( x mult y );
          z = ( x div y )
        }
        """
        is_correct, errors = parse_and_check(source)
        assert is_correct, f"Should pass but got errors: {errors}"
    
    def test_comparison_produces_boolean(self):
        """Comparisons take numeric operands and produce boolean"""
        source = """
        glob { x y }
        proc { }
        func { }
        main {
          var { }
          x = 10;
          if ( x > 5 ) {
            halt
          };
          if ( x eq y ) {
            halt
          }
        }
        """
        is_correct, errors = parse_and_check(source)
        assert is_correct, f"Should pass but got errors: {errors}"
    
    def test_logical_operations(self):
        """Logical operators require boolean operands"""
        source = """
        glob { x y }
        proc { }
        func { }
        main {
          var { }
          if ( ( x > 0 ) and ( y > 0 ) ) {
            halt
          };
          if ( ( x > 0 ) or ( y > 0 ) ) {
            halt
          }
        }
        """
        is_correct, errors = parse_and_check(source)
        assert is_correct, f"Should pass but got errors: {errors}"
    
    def test_unary_operators(self):
        """Test neg (numeric) and not (boolean)"""
        source = """
        glob { x }
        proc { }
        func { }
        main {
          var { }
          x = ( neg 5 );
          if ( not ( x > 0 ) ) {
            halt
          }
        }
        """
        is_correct, errors = parse_and_check(source)
        assert is_correct, f"Should pass but got errors: {errors}"


class TestTypeErrors:
    """Test detection of type errors"""
    
    def test_boolean_in_arithmetic(self):
        """Using boolean where numeric is expected"""
        source = """
        glob { x }
        proc { }
        func { }
        main {
          var { }
          x = ( ( x > 5 ) plus 1 )
        }
        """
        is_correct, errors = parse_and_check(source)
        assert not is_correct, "Should fail: boolean in arithmetic"
        assert any("numeric" in str(e).lower() for e in errors)
    
    def test_numeric_in_while_condition(self):
        """While condition must be boolean"""
        source = """
        glob { x }
        proc { }
        func { }
        main {
          var { }
          x = 5;
          while x {
            halt
          }
        }
        """
        is_correct, errors = parse_and_check(source)
        assert not is_correct, "Should fail: numeric in while condition"
        assert any("boolean" in str(e).lower() for e in errors)
    
    def test_numeric_in_if_condition(self):
        """If condition must be boolean"""
        source = """
        glob { x }
        proc { }
        func { }
        main {
          var { }
          if x {
            halt
          }
        }
        """
        is_correct, errors = parse_and_check(source)
        assert not is_correct, "Should fail: numeric in if condition"
    
    def test_numeric_in_do_until_condition(self):
        """Do-until condition must be boolean"""
        source = """
        glob { x }
        proc { }
        func { }
        main {
          var { }
          do {
            halt
          } until x
        }
        """
        is_correct, errors = parse_and_check(source)
        assert not is_correct, "Should fail: numeric in do-until condition"
    
    def test_not_on_numeric(self):
        """not requires boolean operand"""
        source = """
        glob { x }
        proc { }
        func { }
        main {
          var { }
          if ( not x ) {
            halt
          }
        }
        """
        is_correct, errors = parse_and_check(source)
        assert not is_correct, "Should fail: not on numeric"
    
    def test_and_on_numeric(self):
        """and requires boolean operands"""
        source = """
        glob { a b }
        proc { }
        func { }
        main {
          var { }
          if ( a and b ) {
            halt
          }
        }
        """
        is_correct, errors = parse_and_check(source)
        assert not is_correct, "Should fail: and on numeric"
    
    def test_or_on_numeric(self):
        """or requires boolean operands"""
        source = """
        glob { a b }
        proc { }
        func { }
        main {
          var { }
          if ( a or b ) {
            halt
          }
        }
        """
        is_correct, errors = parse_and_check(source)
        assert not is_correct, "Should fail: or on numeric"
    
    def test_comparison_on_boolean(self):
        """Comparison requires numeric operands"""
        source = """
        glob { x y }
        proc { }
        func { }
        main {
          var { }
          if ( ( x > 0 ) > ( y > 0 ) ) {
            halt
          }
        }
        """
        is_correct, errors = parse_and_check(source)
        assert not is_correct, "Should fail: comparison on boolean"
    
    def test_undeclared_variable(self):
        """Using undeclared variable"""
        source = """
        glob { }
        proc { }
        func { }
        main {
          var { }
          x = 42
        }
        """
        is_correct, errors = parse_and_check(source)
        assert not is_correct, "Should fail: undeclared variable"
        assert any("not declared" in str(e).lower() for e in errors)


class TestProceduresAndFunctions:
    """Test procedure and function type checking"""
    
    def test_procedure_call(self):
        """Procedure calls are correctly typed"""
        source = """
        glob { }
        proc {
          myproc(x y) {
            local { z }
            z = ( x plus y );
            print z
          }
        }
        func { }
        main {
          var { a b }
          a = 10;
          b = 20;
          myproc(a b)
        }
        """
        is_correct, errors = parse_and_check(source)
        assert is_correct, f"Should pass but got errors: {errors}"
    
    def test_function_call(self):
      """Function calls in assignments are correctly typed (return ATOM)"""
      source = """
      glob { }
      proc { }
      func {
        double(n) {
          local { t }
          t = ( n mult 2 );
          halt;
          return t
        }
      }
      main {
        var { x result }
        x = 10;
        result = double(x);
        print result
      }
      """
      is_correct, errors = parse_and_check(source)
      assert is_correct, f"Should pass but got errors: {errors}"

    
    def test_function_return_numeric(self):
      """Function return must be a declared numeric ATOM (negative)"""
      source = """
      glob { n }
      proc { }
      func {
        bad() {
          local { }
          halt;
          return bogus
        }
      }
      main {
        var { }
        halt
      }
      """
      is_correct, errors = parse_and_check(source)
      assert not is_correct, "Should fail: returning an undeclared ATOM"
      assert any("not declared" in str(e).lower() for e in errors)

    
    def test_procedure_with_local_variables(self):
      """Procedures can have local variables; print uses OUTPUT (ATOM)"""
      source = """
      glob { }
      proc {
        calc(a b c) {
          local { x y z }
          x = a;
          y = b;
          z = c;
          z = ( ( x plus y ) plus z );
          print z
        }
      }
      func { }
      main {
        var { }
        calc(1 2 3)
      }
      """
      is_correct, errors = parse_and_check(source)
      assert is_correct, f"Should pass but got errors: {errors}"

    
    def test_function_with_no_params(self):
        """Functions can have no parameters"""
        source = """
        glob { }
        proc { }
        func {
          getzero() {
            local { }
            halt;
            return 0
          }
        }
        main {
          var { x }
          x = getzero();
          print x
        }
        """
        is_correct, errors = parse_and_check(source)
        assert is_correct, f"Should pass but got errors: {errors}"
    
    def test_call_undefined_proc(self):
        """Calling undefined procedure"""
        source = """
        glob { }
        proc { }
        func { }
        main {
          var { }
          undefined(42)
        }
        """
        is_correct, errors = parse_and_check(source)
        assert not is_correct, "Should fail: undefined procedure"
        assert any("not a procedure" in str(e).lower() or "not a function" in str(e).lower() for e in errors)


class TestScoping:
    """Test variable scoping rules"""
    
    def test_global_variable_access(self):
        """Global variables accessible in main"""
        source = """
        glob { g }
        proc { }
        func { }
        main {
          var { }
          g = 42;
          print g
        }
        """
        is_correct, errors = parse_and_check(source)
        assert is_correct, f"Should pass but got errors: {errors}"
    
    def test_global_in_procedure(self):
        """Global variables accessible in procedures"""
        source = """
        glob { g }
        proc {
          setglobal(x) {
            local { }
            g = x;
            print g
          }
        }
        func { }
        main {
          var { }
          setglobal(100)
        }
        """
        is_correct, errors = parse_and_check(source)
        assert is_correct, f"Should pass but got errors: {errors}"
    
    def test_local_variable_scope(self):
        """Local variables only accessible in their scope"""
        source = """
        glob { }
        proc {
          myproc(x) {
            local { y }
            y = ( x plus 1 );
            print y
          }
        }
        func { }
        main {
          var { }
          myproc(10)
        }
        """
        is_correct, errors = parse_and_check(source)
        assert is_correct, f"Should pass but got errors: {errors}"
    
    def test_main_variables(self):
        """Main can declare its own variables"""
        source = """
        glob { }
        proc { }
        func { }
        main {
          var { x y z }
          x = 1;
          y = 2;
          z = ( x plus y );
          print z
        }
        """
        is_correct, errors = parse_and_check(source)
        assert is_correct, f"Should pass but got errors: {errors}"
    
    def test_parameter_as_local(self):
        """Parameters act as local variables"""
        source = """
        glob { }
        proc {
          modify(n) {
            local { }
            n = ( n plus 1 );
            print n
          }
        }
        func { }
        main {
          var { x }
          x = 10;
          modify(x)
        }
        """
        is_correct, errors = parse_and_check(source)
        assert is_correct, f"Should pass but got errors: {errors}"


class TestComplexExpressions:
    """Test complex type checking scenarios"""
    
    def test_nested_arithmetic(self):
        """Nested arithmetic expressions"""
        source = """
        glob { x }
        proc { }
        func { }
        main {
          var { }
          x = ( ( ( 1 plus 2 ) mult 3 ) div 4 )
        }
        """
        is_correct, errors = parse_and_check(source)
        assert is_correct, f"Should pass but got errors: {errors}"
    
    def test_nested_boolean(self):
        """Nested boolean expressions"""
        source = """
        glob { x y }
        proc { }
        func { }
        main {
          var { }
          if ( ( x > 0 ) and ( ( y > 0 ) or ( x eq y ) ) ) {
            halt
          }
        }
        """
        is_correct, errors = parse_and_check(source)
        assert is_correct, f"Should pass but got errors: {errors}"
    
    def test_mixed_valid_expression(self):
        """Mix of comparisons and logical operators"""
        source = """
        glob { a b c }
        proc { }
        func { }
        main {
          var { }
          if ( ( ( a > b ) and ( b > c ) ) or ( a eq c ) ) {
            print "complex"
          }
        }
        """
        is_correct, errors = parse_and_check(source)
        assert is_correct, f"Should pass but got errors: {errors}"
    
    def test_mixed_invalid_expression(self):
        """Invalid mix: arithmetic on boolean"""
        source = """
        glob { x y }
        proc { }
        func { }
        main {
          var { }
          x = ( ( x > y ) plus 1 )
        }
        """
        is_correct, errors = parse_and_check(source)
        assert not is_correct, "Should fail: arithmetic on boolean"
    
    def test_negation_of_arithmetic(self):
        """Negation of arithmetic expression"""
        source = """
        glob { x }
        proc { }
        func { }
        main {
          var { }
          x = ( neg ( x plus 1 ) )
        }
        """
        is_correct, errors = parse_and_check(source)
        assert is_correct, f"Should pass but got errors: {errors}"
    
    def test_not_of_comparison(self):
        """Not of comparison expression"""
        source = """
        glob { x }
        proc { }
        func { }
        main {
          var { }
          if ( not ( x > 0 ) ) {
            halt
          }
        }
        """
        is_correct, errors = parse_and_check(source)
        assert is_correct, f"Should pass but got errors: {errors}"


class TestPrintStatement:
    """Test print statement type checking"""
    
    def test_print_numeric_variable(self):
        """Print numeric variable"""
        source = """
        glob { x }
        proc { }
        func { }
        main {
          var { }
          x = 42;
          print x
        }
        """
        is_correct, errors = parse_and_check(source)
        assert is_correct, f"Should pass but got errors: {errors}"
    
    def test_print_string_literal(self):
        """Print string literal"""
        source = """
        glob { }
        proc { }
        func { }
        main {
          var { }
          print "hello"
        }
        """
        is_correct, errors = parse_and_check(source)
        assert is_correct, f"Should pass but got errors: {errors}"
    
    def test_print_number_literal(self):
        """Print number literal"""
        source = """
        glob { }
        proc { }
        func { }
        main {
          var { }
          print 42
        }
        """
        is_correct, errors = parse_and_check(source)
        assert is_correct, f"Should pass but got errors: {errors}"


class TestLoops:
    """Test loop type checking"""
    
    def test_while_loop_valid(self):
        """While loop with boolean condition"""
        source = """
        glob { x }
        proc { }
        func { }
        main {
          var { }
          x = 10;
          while ( x > 0 ) {
            x = ( x minus 1 );
            print x
          }
        }
        """
        is_correct, errors = parse_and_check(source)
        assert is_correct, f"Should pass but got errors: {errors}"
    
    def test_do_until_loop_valid(self):
        """Do-until loop with boolean condition"""
        source = """
        glob { x }
        proc { }
        func { }
        main {
          var { }
          x = 0;
          do {
            x = ( x plus 1 );
            print x
          } until ( x eq 10 )
        }
        """
        is_correct, errors = parse_and_check(source)
        assert is_correct, f"Should pass but got errors: {errors}"
    
    def test_nested_loops(self):
        """Nested loops"""
        source = """
        glob { i j }
        proc { }
        func { }
        main {
          var { }
          i = 5;
          while ( i > 0 ) {
            j = 5;
            while ( j > 0 ) {
              j = ( j minus 1 )
            };
            i = ( i minus 1 )
          }
        }
        """
        is_correct, errors = parse_and_check(source)
        assert is_correct, f"Should pass but got errors: {errors}"


class TestBranches:
    """Test branch (if) type checking"""
    
    def test_if_without_else(self):
        """If statement without else"""
        source = """
        glob { x }
        proc { }
        func { }
        main {
          var { }
          if ( x > 0 ) {
            print "positive"
          }
        }
        """
        is_correct, errors = parse_and_check(source)
        assert is_correct, f"Should pass but got errors: {errors}"
    
    def test_if_with_else(self):
        """If statement with else"""
        source = """
        glob { x }
        proc { }
        func { }
        main {
          var { }
          if ( x > 0 ) {
            print "positive"
          } else {
            print "nonpositive"
          }
        }
        """
        is_correct, errors = parse_and_check(source)
        assert is_correct, f"Should pass but got errors: {errors}"
    
    def test_nested_if(self):
        """Nested if statements"""
        source = """
        glob { x y }
        proc { }
        func { }
        main {
          var { }
          if ( x > 0 ) {
            if ( y > 0 ) {
              print "bothpositive"
            } else {
              print "xpositiveynot"
            }
          } else {
            print "xnotpositive"
          }
        }
        """
        is_correct, errors = parse_and_check(source)
        assert is_correct, f"Should pass but got errors: {errors}"


class TestIntegration:
    """Integration tests with complete programs"""
    
    def test_complete_program(self):
        """Complete program with all features"""
        source = """
        glob { g counter }
        proc {
          increment() {
            local { }
            counter = ( counter plus 1 );
            print counter
          }
        }
        func {
          double(n) {
            local { result }
            result = ( n mult 2 );
            halt;
            return result
          }
          
          iszero(x) {
            local { }
            halt;
            return x
          }
        }
        main {
          var { x y temp }
          g = 100;
          counter = 0;
          x = 10;
          y = 20;
          
          temp = double(x);
          print temp;
          
          increment();
          increment();
          
          if ( x > y ) {
            print "xgreater"
          } else {
            print "ygreaterorequal"
          };
          
          while ( counter > 0 ) {
            counter = ( counter minus 1 )
          };
          
          do {
            x = ( x plus 1 )
          } until ( x eq 15 )
        }
        """
        is_correct, errors = parse_and_check(source)
        assert is_correct, f"Should pass but got errors: {errors}"
    
    def test_program_with_multiple_errors(self):
        """Program with multiple type errors"""
        source = """
        glob { x }
        proc { }
        func { }
        main {
          var { y }
          x = ( ( x > 0 ) plus 1 );
          while y {
            halt
          };
          if ( not x ) {
            halt
          }
        }
        """
        is_correct, errors = parse_and_check(source)
        assert not is_correct, "Should fail with multiple errors"
        assert len(errors) >= 3, f"Expected at least 3 errors, got {len(errors)}"