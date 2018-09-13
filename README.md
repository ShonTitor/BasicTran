# BasicTran
Integrantes: 14-10820 14-10576  

Para la cuarta fase del proyecto de Traductores e Interpretadores se esperaba que realizáramos  
un programa que ejecute el código de BasicTran y además verifique errores de carácter dinámico   
como lo es un ciclo for que iteraría indefinidamente o un índice inválido para un arreglo.  
  
Para el propósito de ejecutar el código se le asignó a cada nodo del árbol un atributo "codigo" que contiene  
su equivalente en python. Por ejemplo, el nodo correspondiente a una asignación "a <- 5;" contendrá "a=5".  
El método "ejecutar" recorre el árbol sintáctico recursivamente verificando errores dinámicos y llamando a  
la función "exec" para efectuar las instrucciones. En caso de haber un error se indica la línea y se aborta.  
  
Para concluir, se probaron varios programas escritos por nosotros y se verificó que corrieran como se esperaría  
en cualquier otro lenguaje de programación. Asi se comprobó que las verificaciones dinámicas daban los   
resultados esperados y se concluyó que el programa era correcto y completo.  

## Para ejecutar  
Lex <script>  
Donde <script> es el programa escrito en BasicTran. 
Nota: Para correr el bash script hay que darle permiso de ejecución con el comando chmod.  
Alternativamente python3 BasicTran.py <script>
