% Parent-child facts
parent(john, mary).
parent(john, tom).
parent(susan, mary).
parent(susan, tom).
parent(mary, alice).
parent(mary, bob).

% Gender facts
male(john).
male(tom).
male(bob).
female(susan).
female(mary).
female(alice).

% Rules
father(X, Y) :- parent(X, Y), male(X).
mother(X, Y) :- parent(X, Y), female(X).
sibling(X, Y) :- parent(Z, X), parent(Z, Y), X \= Y.