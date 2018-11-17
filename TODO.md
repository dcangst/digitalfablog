# TO DO

- [] Fablog bookings
  - [x] generate bookings to new account_to field
  - [] only generate bookings once full amount is payed. (change 'Close Fablog' button if not full amount)
    - new model payment: register payments until full amount is payed then generate bookings
  - [] rewrite booking logic:
      - change FinancialAccount to Journal, because this is not intended to do the full accounting
      - Bank Accout will also be a Journal but thats ok (since they are ;)
      - a booking will be:
        - a cash count: amount 0, updates true balance
        - a true booking, eiter positive (income) or negative (spending). the account in the booking will therefore represent eiter the credit (haben) for income or the debit (soll)
  - [] add bookings in post_save signals to cashcount
    - [x] CashCount
    - [] Fablog

- [] implement workshops
  - 'special' tab, workshop similar to fabday?

- [] implement expenses
  - 'special' fablog?

- [] member interface
  - [] Overview
  - [] edit view for members

- [] machines interface
  - [] enter new machines
  - [] machine status

- [] material interface

- [] Gutscheine

- [] weitere fablog positionen

