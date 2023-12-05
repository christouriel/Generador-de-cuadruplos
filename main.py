import tkinter as tk
from tkinter import ttk, messagebox, filedialog

class Nodo:
    contador_id = 0

    @classmethod
    def reset_contador(cls):
        cls.contador_id = 0

    def __init__(self, tipo, valor=None, izquierdo=None, derecho=None):
        self.tipo = tipo
        self.valor = valor
        self.izquierdo = izquierdo
        self.derecho = derecho
        self.id = Nodo.contador_id
        Nodo.contador_id += 1

def analizador_lexico(expresion):
    tokens = []
    i = 0
    while i < len(expresion):
        if expresion[i].isalpha():
            j = i
            while j < len(expresion) and (expresion[j].isalpha() or expresion[j].isdigit()):
                j += 1
            tokens.append(("id", expresion[i:j]))
            i = j
        elif expresion[i].isdigit():
            j = i
            while j < len(expresion) and expresion[j].isdigit():
                j += 1
            tokens.append(("num", expresion[i:j]))
            i = j
        elif expresion[i] in "+-*/()=":
            tokens.append((expresion[i],))
            i += 1
        elif expresion[i:i+2] == "==":
            tokens.append(("==",))
            i += 2
        elif expresion[i:i+2] == ">=":
            tokens.append((">=",))
            i += 2
        elif expresion[i:i+2] == "<=":
            tokens.append(("<=",))
            i += 2
        elif expresion[i] == ">":
            tokens.append((">",))
            i += 1
        elif expresion[i] == "<":
            tokens.append(("<",))
            i += 1
        elif expresion[i:i+5].lower() == "while":
            tokens.append(("while",))
            i += 5
        elif expresion[i:i+7].lower() == "endwhile":
            tokens.append(("endwhile",))
            i += 7
        elif expresion[i:i+2].lower() == "if":
            tokens.append(("if",))
            i += 2
        elif expresion[i:i+6].lower() == "endif":
            tokens.append(("endif",))
            i += 6
        else:
            raise ValueError("Carácter no válido: " + expresion[i])
    return tokens

def analizador_sintactico(tokens):
    def factor():
        if not tokens:
            raise ValueError("Error de sintaxis: Expresión incompleta.")

        token = tokens.pop(0)
        if token[0] == "id":
            return Nodo("id", token[1])
        elif token[0] == "num":
            return Nodo("num", token[1])
        elif token[0] == "=":
            id_token = tokens.pop(0)
            if tokens and tokens[0][0] in ("id", "num"):
                value_token = tokens.pop(0)
                return Nodo("=", id_token[1], Nodo(value_token[0], value_token[1]))
            else:
                raise ValueError("Error de sintaxis: Se esperaba un identificador o número después de '='.")
        elif token[0] in ("==", "<", ">", "<=", ">="):
            arg1 = factor()
            arg2 = factor()
            return Nodo(token[0], None, arg1, arg2)
        elif token[0] == "(":
            expr = expresion()
            if tokens and tokens[0][0] == ")":
                tokens.pop(0)
                return expr
            else:
                raise ValueError("Paréntesis de cierre faltante.")
        else:
            raise ValueError("Token no válido: " + token[0])

    def termino():
        nodo = factor()
        while tokens and tokens[0][0] in ("*", "/"):
            operador = tokens.pop(0)
            arg2 = factor()
            nodo = Nodo(operador[0], None, nodo, arg2)
        return nodo

    def expresion():
        nodo = termino()
        while tokens and tokens[0][0] in ("+", "-"):
            operador = tokens.pop(0)
            arg2 = termino()
            nodo = Nodo(operador[0], None, nodo, arg2)
        return nodo

    def bucle_while():
        if not tokens:
            raise ValueError("Error de sintaxis: 'while' sin condición correspondiente.")

        tokens.pop(0)  # consume "while"
        condicion = expresion()
        if not tokens:
            raise ValueError("Error de sintaxis: Se esperaba 'endwhile' pero la expresión terminó.")

        if tokens[0][0] == "endwhile":
            tokens.pop(0)  # consume "endwhile"
        else:
            raise ValueError("Error de sintaxis: Se esperaba 'endwhile'.")
        return Nodo("while", None, condicion)

    def estructura_if():
        if not tokens:
            raise ValueError("Error de sintaxis: 'if' sin condición correspondiente.")

        tokens.pop(0)  # consume "if"
        condicion = expresion()
        if not tokens:
            raise ValueError("Error de sintaxis: Se esperaba 'endif' pero la expresión terminó.")

        if tokens[0][0] == "endif":
            tokens.pop(0)  # consume "endif"
        else:
            raise ValueError("Error de sintaxis: Se esperaba 'endif'.")
        return Nodo("if", None, condicion)

    nodo = None
    while tokens:
        token = tokens.pop(0)
        if token[0] == "while":
            if nodo is not None:
                raise ValueError("Error de sintaxis: Se encontró 'while' sin 'endwhile' correspondiente.")
            nodo = bucle_while()
        elif token[0] == "endwhile":
            raise ValueError("Error de sintaxis: Se encontró 'endwhile' sin 'while' correspondiente.")
        elif token[0] == "if":
            if nodo is not None:
                raise ValueError("Error de sintaxis: Se encontró 'if' sin 'endif' correspondiente.")
            nodo = estructura_if()
        elif token[0] == "endif":
            raise ValueError("Error de sintaxis: Se encontró 'endif' sin 'if' correspondiente.")
        else:
            tokens.insert(0, token)  # Devuelve el token para que sea procesado como expresión
            expresion_nodo = expresion()
            if nodo is None:
                nodo = expresion_nodo
            else:
                nodo = Nodo("expresion", None, nodo, expresion_nodo)
    return nodo

def generar_cuadruplos(nodo, cuadruplos):
    if nodo is not None:
        if nodo.tipo in ["+", "-", "*", "/"]:
            arg1 = nodo.izquierdo.valor if nodo.izquierdo.tipo in ["num","id"] else 't' + str(nodo.izquierdo.id)
            arg2 = nodo.derecho.valor if nodo.derecho.tipo in ["num","id"] else 't' + str(nodo.derecho.id)
            resultado = 't' + str(nodo.id)
            cuadruplos.append([nodo.tipo, arg1, arg2, resultado])
        elif nodo.tipo in ["num","id"]:
            resultado = 't' + str(nodo.id)
            cuadruplos.append([nodo.tipo, nodo.valor, 'None', resultado])
        elif nodo.tipo == "while":
            cuadruplos.append(["while", nodo.izquierdo])
        generar_cuadruplos(nodo.izquierdo, cuadruplos)
        generar_cuadruplos(nodo.derecho, cuadruplos)

def mostrar_cuadruplos_en_interfaz(cuadruplos):
    # Borrar todas las filas existentes
    tabla_cuadruplos.delete(*tabla_cuadruplos.get_children())

    # Insertar todas las filas nuevamente
    for cuadruplo in cuadruplos:
        if cuadruplo[0] == "while":
            tabla_cuadruplos.insert('', 'end', values=("while", cuadruplo[1]))
        else:
            tabla_cuadruplos.insert('', 'end', values=(cuadruplo[0], cuadruplo[1], cuadruplo[2], cuadruplo[3]))

def limpiar_tablas():
    tabla_cuadruplos.delete(*tabla_cuadruplos.get_children())

# Lista global para almacenar todos los cuádruplos
todos_cuadruplos = []

def procesar_expresiones(cadenas):
    global todos_cuadruplos
    todos_cuadruplos = []

    for expresion in cadenas:
        try:
            tokens = analizador_lexico(expresion)
            if len(tokens) > 0 and tokens[0][0] in ("+", "-", "*", "/"):
                raise ValueError("La cadena no puede empezar con un operador.")

            prev_token = None
            for token in tokens:
                if prev_token and prev_token[0] in ("+", "-", "*", "/") and token[0] in ("+", "-", "*", "/"):
                    raise ValueError("No pueden haber dos operadores consecutivos en la cadena.")
                prev_token = token

            resultado = analizador_sintactico(tokens)
            cuadruplos = []
            generar_cuadruplos(resultado, cuadruplos)
            todos_cuadruplos.extend(cuadruplos)

            resultado_label.config(text="Cadena válida")
            messagebox.showinfo("Validación Exitosa", "La cadena es válida.")
        except Exception as e:
            resultado_label.config(text=f"Error: {str(e)}")
            messagebox.showerror("Error de Validación", f"La cadena no es válida")
            limpiar_tablas()

        Nodo.reset_contador()

def validar_expresion():
    expresiones = entrada.get("1.0", tk.END).splitlines()
    procesar_expresiones(expresiones)

def procesar_expresiones_desde_archivo(archivo):
    try:
        with open(archivo, 'r') as file:
            expresiones = file.readlines()
            procesar_expresiones([expresion.strip() for expresion in expresiones])
    except Exception as e:
        messagebox.showerror("Error de Archivo", f"No se pudo leer el archivo:\n{str(e)}")

def cargar_desde_archivo():
    file_path = filedialog.askopenfilename(title="Seleccione un archivo de texto", filetypes=[("Archivos de texto", "*.txt")])
    if file_path:
        procesar_expresiones_desde_archivo(file_path)

def limpiar_cuadro():
    entrada.delete("1.0", tk.END)
    resultado_label.config(text="")
    limpiar_tablas()

def mostrar_cuadruplos():
  ventana_cuadruplos = tk.Toplevel(ventana)
  ventana_cuadruplos.title("Tabla de Cuádruplos")

  tabla_cuadruplos_popup = ttk.Treeview(ventana_cuadruplos, columns=("OP", "ARG1", "ARG2", "Resultado"), show="headings")
  tabla_cuadruplos_popup.heading("OP", text="OP")
  tabla_cuadruplos_popup.heading("ARG1", text="ARG1")
  tabla_cuadruplos_popup.heading("ARG2", text="ARG2")
  tabla_cuadruplos_popup.heading("Resultado", text="Resultado")

  for cuadruplo in todos_cuadruplos:
      if cuadruplo[0] == "while":
          tabla_cuadruplos_popup.insert('', 'end', values=("while", cuadruplo[1]))
      else:
          tabla_cuadruplos_popup.insert('', 'end', values=(cuadruplo[0], cuadruplo[1], cuadruplo[2], cuadruplo[3]))

  tabla_cuadruplos_popup.pack(pady=10)

def generar_codigo_intermedio(cuadruplos):
  codigo_intermedio.clear()

  for cuadruplo in cuadruplos:
      if cuadruplo[0] == "while":
          codigo_intermedio.append(f"while {cuadruplo[1]}:")
      else:
          codigo_intermedio.append(f"{cuadruplo[3]} = {cuadruplo[1]} {cuadruplo[0]} {cuadruplo[2]}")

def mostrar_codigo_intermedio():
  ventana_codigo_intermedio = tk.Toplevel(ventana)
  ventana_codigo_intermedio.title("Código Intermedio")

  codigo_intermedio_text = tk.Text(ventana_codigo_intermedio, height=10, width=50, bg="white", fg="black")
  for instruccion in codigo_intermedio:
      codigo_intermedio_text.insert(tk.END, instruccion + "\n")
  codigo_intermedio_text.pack()

def mostrar_codigo_intermedio():
   global todos_cuadruplos
   generar_codigo_intermedio(todos_cuadruplos)

   ventana_codigo_intermedio = tk.Toplevel(ventana)
   ventana_codigo_intermedio.title("Código Intermedio")

   codigo_intermedio_text = tk.Text(ventana_codigo_intermedio, height=10, width=50, bg="white", fg="black")
   for instruccion in codigo_intermedio:
       codigo_intermedio_text.insert(tk.END, instruccion + "\n")
   codigo_intermedio_text.pack()

ventana = tk.Tk()
ventana.title("Generador de Cuadruplos")
ventana.geometry("800x600")  # Aumentar altura de la ventana

# Cambiar el color de fondo de la ventana principal
ventana.configure(bg="magenta")

# Usar el estilo de fuente en cursiva para el título
titulo_label = tk.Label(ventana, text="Analizador Sintáctico", font=("Arial", 16, "italic"), bg="magenta", fg="white")
titulo_label.pack(pady=10)

entrada = tk.Text(ventana, height=10, width=50, bg="white", fg="black")
entrada.pack()

validar_button = tk.Button(ventana, text="Analizar", command=validar_expresion, bg="purple", fg="white")
validar_button.pack(pady=10)

cargar_button = tk.Button(ventana, text="Cargar desde archivo", command=cargar_desde_archivo, bg="darkmagenta", fg="white")
cargar_button.pack(pady=10)

limpiar_button = tk.Button(ventana, text="Limpiar", command=limpiar_cuadro, bg="hotpink", fg="white")
limpiar_button.pack(pady=10)

mostrar_cuadruplos_button = tk.Button(ventana, text="Mostrar Cuádruplos", command=mostrar_cuadruplos, bg="magenta", fg="white")
mostrar_cuadruplos_button.pack(pady=10)

ver_codigo_intermedio_button = tk.Button(ventana, text="Ver Código Intermedio", command=mostrar_codigo_intermedio, bg="magenta", fg="white")
ver_codigo_intermedio_button.pack(pady=10)

resultado_label = tk.Label(ventana, text="", font=("Arial", 12), height=2, bg="magenta", fg="white")
resultado_label.pack()

ventana.mainloop()
