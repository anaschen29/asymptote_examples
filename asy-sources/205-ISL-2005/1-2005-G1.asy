Given a triangle $ABC$ satisfying $AC+BC=3\cdot AB$. The incircle of triangle $ABC$ has center $I$ and touches the sides $BC$ and $CA$ at the points $D$ and $E$, respectively. 
Let $K$ and $L$ be the reflections of the points $D$ and $E$ with respect to $I$. Prove that the points $A$, $B$, $K$, $L$ lie on one circle.


Asympote_Cod_Below:

pair B = origin;
pair C = (4,0);
pair A = 3*dir(35.430945);

pair I = incenter(A,B,C);
pair D = foot(I,B,C);
pair E = foot(I,A,B);

pair K = 2*I-D;
pair L = 2*I-E;

draw(A--B--C--cycle);
draw(incircle(A, B, C), grey);

dot("$A$",A,dir(90));
dot("$B$",B,dir(200));
dot("$C$",C,dir(-40));

dot("$I$",I,dir(120));
dot("$D$",D,dir(-90));
dot("$E$",E,dir(120));

dot("$K$",K,S);
dot("$L$",L,dir(90));


/*
    Source: Shortlist 2005 G1
    Points: A B C D E I K L
    Item: D K I
    Item: L I E
    Item: B D I E
    Item: A C K I L
    Text: $AB+BC=3AC$.
    Text: $K$ and $L$ are reflections.
*/
