is_member(X,[X|_]):-!.

is_member(X,[_|T]):-is_member(X,T).

list_length([],0):-!.

list_length([_|T],N):-
    list_length(T,N1),
    N is N1+1.