# foney: Money Calculator

## Currently supports

* Money literals: 
    * Postfixed: `1$, 2Br, 1USD, 2BYN`
    * Prefixed: `$1, Br2, USD1, BYN2`

* Arithmetical operations on Money and Number (numbers are always float)
    * `1$ + 2Br` (result is Money in USD) 
    * `1$ * 3` (result is Money in USD)
    * `1 * 2` (result is Number)

* Variables
    * `a = 5`
    * `b = Br5`
    * `c = a * b`
    * `d = e = c`
