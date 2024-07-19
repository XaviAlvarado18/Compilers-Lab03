grammar ConfRoomScheduler;

prog: (stat NEWLINE)* stat? ;

stat: reserve                 # reserveStat
    | cancel                  # cancelStat
    | list                    # listStat
    |                         # blank
    ;

reserve: 'RESERVA' USER 'SALA' ID 'PARA' DATE 'DE' TIME 'A' TIME ; 

cancel: 'CANCELAR' ID 'PARA' DATE 'DE' TIME 'A' TIME ; 

list: 'LISTAR' ; 

DATE: DIGIT DIGIT '/' DIGIT DIGIT '/' DIGIT DIGIT DIGIT DIGIT ; 
TIME: DIGIT DIGIT ':' DIGIT DIGIT ; 
ID  : [0-9]+ ;
USER: [a-zA-Z]+ ; 
NEWLINE: '\r'? '\n' ; 
WS  : [ \t]+ -> skip ; 

fragment DIGIT: [0-9] ;