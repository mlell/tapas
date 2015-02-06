library(argparse)

expected="
a1 | numeric   | <>  | Erster Operand
a2 | numeric   | <>  | Zweiter Operand
m  | character | sum | Funktion,die angewendet werden soll
"

a= parseArguments(expected)

if(a$m == "mul") {
    print("Performing multiplication")
    print(a$a1 * a$a2)
}else {
    print("Performing summation")
    print(a$a1 + a$a2)
}

