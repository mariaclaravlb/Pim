import os, sys, ctypes
from ctypes import c_char_p, c_int, create_string_buffer
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, simpledialog
from tkinter import font as tkfont
import re

LIB_NAME = "backend.dll" if sys.platform.startswith("win") else "backend.so"
backend = ctypes.CDLL(os.path.join(os.getcwd(), LIB_NAME))

# ==== Bindings ====
backend.inicializar_arquivos.restype = None
backend.inicializar_arquivos()

backend.salvar_usuario.argtypes = [c_char_p, c_char_p, c_char_p, c_char_p]
backend.salvar_usuario.restype = c_int

backend.autenticar.argtypes = [c_char_p, c_char_p, c_char_p, c_int]
backend.autenticar.restype = c_int

backend.criar_turma.argtypes = [c_char_p, c_char_p, c_char_p, c_char_p, c_int]
backend.criar_turma.restype = c_int

backend.listar_turmas.argtypes = [c_char_p, c_int]
backend.listar_turmas.restype = c_int

backend.criar_atividade.argtypes = [c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_char_p]
backend.criar_atividade.restype = c_int

backend.listar_atividades.argtypes = [c_char_p, c_int]
backend.listar_atividades.restype = c_int

backend.entregar_atividade.argtypes = [c_char_p, c_char_p]
backend.entregar_atividade.restype = c_int

backend.matricular_aluno.argtypes = [c_char_p, c_char_p, c_char_p]
backend.matricular_aluno.restype = c_int

backend.listar_alunos_da_turma.argtypes = [c_char_p, c_char_p, c_int]
backend.listar_alunos_da_turma.restype = c_int

backend.listar_turmas_do_aluno.argtypes = [c_char_p, c_char_p, c_int]
backend.listar_turmas_do_aluno.restype = c_int

backend.lancar_nota.argtypes = [c_char_p, c_char_p, c_char_p, c_char_p, c_char_p]
backend.lancar_nota.restype = c_int

backend.consultar_notas_aluno.argtypes = [c_char_p, c_char_p, c_int]
backend.consultar_notas_aluno.restype = c_int

backend.boletim_aluno.argtypes = [c_char_p, c_char_p, c_int]
backend.boletim_aluno.restype = c_int

backend.salvar_meta_atividade.argtypes = [c_char_p, c_char_p, c_char_p]
backend.salvar_meta_atividade.restype = c_int

backend.registrar_entrega_meta.argtypes = [c_char_p, c_char_p, c_char_p, c_char_p]
backend.registrar_entrega_meta.restype = c_int

backend.salvar_turma_qtd_atividades.argtypes = [c_char_p, c_int]
backend.salvar_turma_qtd_atividades.restype = c_int


# ==== Wrappers ====
def salvar_meta_atividade_c(atividade_id, codigo_folha, data_lanc):
    r = backend.salvar_meta_atividade(atividade_id.encode(),
                                      (codigo_folha or "-").encode(),
                                      (data_lanc or "-").encode())
    return r == 0

def registrar_entrega_meta_c(atividade_id, aluno_login, codigo_folha, data_lanc):
    r = backend.registrar_entrega_meta(atividade_id.encode(), aluno_login.encode(),
                                       (codigo_folha or "-").encode(), (data_lanc or "-").encode())
    return r == 0

def salvar_turma_qtd_atividades_c(turma_id, qtd):
    r = backend.salvar_turma_qtd_atividades(turma_id.encode(), int(qtd))
    return r == 0

def salvar_usuario_c(login, nome, senha, tipo):
    r = backend.salvar_usuario(login.encode(), nome.encode(), senha.encode(), tipo.encode())
    return (True, "Usuário salvo com sucesso.") if r==0 else \
           (False, "Login já existe.") if r==1 else \
           (False, "Erro ao salvar usuário.")

def autenticar_c(login, senha):
    buf = create_string_buffer(64)
    r = backend.autenticar(login.encode(), senha.encode(), buf, ctypes.sizeof(buf))
    if r==0: return True, buf.value.decode()
    if r==1: return False, "Login não encontrado."
    if r==2: return False, "Senha incorreta."
    return False, "Erro de autenticação."

def criar_turma_c(id_, nome, desc, prof_login, capacidade):
    r = backend.criar_turma(id_.encode(), nome.encode(), (desc or "").encode(),
                            (prof_login or "").encode(), int(capacidade))
    if r==0: return True, "Turma criada."
    if r==1: return False, "ID de turma já existe."
    return False, "Sem permissão ou erro ao criar turma."

def listar_turmas_c():
    buf = create_string_buffer(8192)
    r = backend.listar_turmas(buf, ctypes.sizeof(buf))
    if r==0: return buf.value.decode()
    if r==1: return "Resultado muito grande; aumente buffer."
    return "Erro ao listar turmas."

def _turmas_do_aluno(login):
    texto = listar_turmas_do_aluno_c(login)
    ids = [l.strip() for l in texto.splitlines()
           if l.strip() and "matr" not in l.lower() and "nenhum" not in l.lower()]
    return set(ids)

def criar_atividade_c(id_, turma_id, titulo, descricao, prazo, autor_login):
    r = backend.criar_atividade(id_.encode(), turma_id.encode(), titulo.encode(),
                                (descricao or "").encode(), (prazo or "").encode(),
                                (autor_login or "").encode())
    return (True, "Atividade criada.") if r==0 else (False, "Sem permissão ou erro ao criar atividade.")

def listar_atividades_c():
    buf = create_string_buffer(16384)
    r = backend.listar_atividades(buf, ctypes.sizeof(buf))
    if r==0: return buf.value.decode()
    if r==1: return "Resultado muito grande; aumente buffer."
    return "Erro ao listar atividades."

def entregar_atividade_c(atividade_id, aluno_login):
    r = backend.entregar_atividade(atividade_id.encode(), aluno_login.encode())
    if r==0: return True, "Entrega registrada."
    if r==1: return False, "Atividade não encontrada."
    return False, "Erro ou sem permissão/matrícula."

def matricular_aluno_c(turma_id, aluno_login, actor_login):
    r = backend.matricular_aluno(turma_id.encode(), aluno_login.encode(), actor_login.encode())
    return (True, "Aluno matriculado.") if r==0 else \
           (False, "Turma lotada.") if r==1 else \
           (False, "Turma não encontrada/erro.") if r==2 else \
           (False, "Aluno já matriculado.") if r==3 else \
           (False, "Aluno inexistente.") if r==4 else \
           (False, "Sem permissão.") if r==6 else \
           (False, "Erro ao matricular.")

def listar_alunos_turma_c(turma_id):
    buf = create_string_buffer(8192)
    r = backend.listar_alunos_da_turma(turma_id.encode(), buf, ctypes.sizeof(buf))
    if r==0: return buf.value.decode()
    if r==1: return "Resultado muito grande; aumente buffer."
    return "Erro ao listar alunos da turma."

def listar_turmas_do_aluno_c(aluno_login):
    buf = create_string_buffer(8192)
    r = backend.listar_turmas_do_aluno(aluno_login.encode(), buf, ctypes.sizeof(buf))
    if r==0: return buf.value.decode()
    if r==1: return "Resultado muito grande; aumente buffer."
    return "Erro ao listar suas turmas."

def lancar_nota_c(turma_id, aluno_login, disciplina, nota, actor_login):
    r = backend.lancar_nota(turma_id.encode(), aluno_login.encode(), disciplina.encode(), nota.encode(), actor_login.encode())
    return (True, "Nota lançada.") if r==0 else \
           (False, "Dados inválidos.") if r==2 else \
           (False, "Aluno inexistente.") if r==4 else \
           (False, "Aluno não matriculado na turma.") if r==5 else \
           (False, "Sem permissão.") if r==6 else \
           (False, "Erro ao lançar nota.")

def consultar_notas_c(aluno_login):
    buf = create_string_buffer(16384)
    r = backend.consultar_notas_aluno(aluno_login.encode(), buf, ctypes.sizeof(buf))
    if r==0: return buf.value.decode()
    if r==1: return "Resultado muito grande; aumente buffer."
    return "Erro ao consultar notas."

def boletim_c(aluno_login):
    buf = create_string_buffer(16384)
    r = backend.boletim_aluno(aluno_login.encode(), buf, ctypes.sizeof(buf))
    if r==0: return buf.value.decode()
    if r==1: return "Resultado muito grande; aumente buffer."
    return "Erro ao consultar boletim."

# ==== App Tkinter ====
def ia_responder(pergunta: str) -> str:
    if not pergunta:
        return "Faça uma pergunta. 🙂"
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        return "IA desativada: defina a variável de ambiente OPENAI_API_KEY."
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        resp = client.chat.completions.create(
            model="gpt-4o-mini", 
            messages=[
                {"role": "system", "content": "Você é um assistente educacional simples. Responda de forma clara, breve e em português do Brasil."},
                {"role": "user", "content": pergunta}
            ],
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"Erro na IA: {e}"
    
class App:
    def __init__(self, root):
        self.root = root
        root.title("Sistema Acadêmico")
        root.geometry("1024x720")
        root.minsize(800, 600)
        root.rowconfigure(0, weight=1)
        root.columnconfigure(0, weight=1)

        default_font = tkfont.nametofont("TkDefaultFont")
        default_font.configure(size=11)

        self.setup_style()  

        self.current_user = None
        self.build_login()

    def setup_style(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except:
            pass

        self.root.configure(bg="#e5e7eb") 

        style.configure("App.TFrame", background="#e5e7eb")

        style.configure(
            "Card.TFrame",
            background="white",
            relief="raised",
            borderwidth=1
        )

        style.configure(
            "Title.TLabel",
            font=("Segoe UI", 16, "bold"),
            background="#e5e7eb"
        )
        style.configure(
            "CardTitle.TLabel",
            font=("Segoe UI", 12, "bold"),
            background="white"
        )
        style.configure(
            "Section.TLabel",
            font=("Segoe UI", 11, "bold"),
            background="#e5e7eb"
        )

        style.configure("TButton", padding=6)

        style.configure(
            "Accent.TButton",
            padding=6
        )
        style.map(
            "Accent.TButton",
            background=[("!disabled", "#2563eb"), ("pressed", "#1d4ed8")],
            foreground=[("!disabled", "white")]
        )

        # Notebook (abas)
        style.configure("TNotebook", background="#e5e7eb", borderwidth=0)
        style.configure("TNotebook.Tab", padding=(12, 6))
    
            # ---------- LOGIN ----------
    def build_login(self):
        for w in self.root.winfo_children():
            w.destroy()

        container = ttk.Frame(self.root, style="App.TFrame", padding=20)
        container.pack(fill=tk.BOTH, expand=True)

        # centralizar o card de login
        container.columnconfigure(0, weight=1)
        container.rowconfigure(0, weight=1)

        card = ttk.Frame(container, style="Card.TFrame", padding=20)
        card.grid(row=0, column=0, sticky="nsew")

        for i in range(2):
            card.columnconfigure(i, weight=1)

        ttk.Label(
            card,
            text="Login do Sistema Acadêmico",
            style="CardTitle.TLabel"
        ).grid(row=0, column=0, columnspan=2, pady=(0, 16))

        ttk.Label(card, text="Login:", background="white").grid(row=1, column=0, sticky=tk.E, pady=4, padx=(0, 6))
        self.login_entry = ttk.Entry(card)
        self.login_entry.grid(row=1, column=1, sticky="ew", pady=4)

        ttk.Label(card, text="Senha:", background="white").grid(row=2, column=0, sticky=tk.E, pady=4, padx=(0, 6))
        self.senha_entry = ttk.Entry(card, show="*")
        self.senha_entry.grid(row=2, column=1, sticky="ew", pady=4)

        btn_frame = ttk.Frame(card, style="Card.TFrame")
        btn_frame.grid(row=3, column=0, columnspan=2, pady=(14, 0))

        ttk.Button(btn_frame, text="Entrar", style="Accent.TButton",
                   command=self.tentar_login).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(btn_frame, text="Registrar (admin apenas)",
                   command=self.registrar_usuario_prompt).pack(side=tk.LEFT)

        self.senha_entry.bind("<Return>", lambda e: self.tentar_login())


    def tentar_login(self):
        login = self.login_entry.get().strip()
        senha = self.senha_entry.get().strip()
        ok, resp = autenticar_c(login, senha)
        if ok:
            self.current_user = (login, resp)  # resp = tipo
            messagebox.showinfo("OK", f"Autenticado como {resp}")
            self.build_main()
        else:
            messagebox.showerror("Erro", resp)

    def registrar_usuario_prompt(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Registrar usuário (Admin)")
        dialog.geometry("420x260")
        for i in range(2):
            dialog.columnconfigure(i, weight=1)

        campos = ["Nome", "Login", "Senha", "Tipo (admin/professor/aluno)"]
        entradas = []

        for i, campo in enumerate(campos):
            ttk.Label(dialog, text=campo + ":").grid(row=i, column=0, sticky=tk.E, pady=3)
            e = ttk.Entry(dialog)
            e.grid(row=i, column=1, sticky="ew", pady=3)
            entradas.append(e)

        def salvar():
            nome, login, senha, tipo = [e.get().strip() for e in entradas]
            if tipo not in ("admin","professor","aluno"):
                messagebox.showerror("Erro", "Tipo inválido. Use admin/professor/aluno.")
                return
            ok, msg = salvar_usuario_c(login, nome, senha, tipo)
            messagebox.showinfo("Resultado", msg)
            if ok:
                dialog.destroy()

        ttk.Button(dialog, text="Salvar", command=salvar).grid(row=4, column=0, columnspan=2, pady=8)

    # ---------- MAIN ----------
    def build_main(self):
        for w in self.root.winfo_children():
            w.destroy()
        login, tipo = self.current_user

        menubar = tk.Menu(self.root)
        menubar.add_command(label="Sair", command=self.logout)
        self.root.config(menu=menubar)

        root_frame = ttk.Frame(self.root, style="App.TFrame", padding=10)
        root_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(
            root_frame,
            text=f"Usuário: {login} ({tipo})",
            style="Title.TLabel"
        ).pack(anchor=tk.W, pady=(0, 10))

        pan = ttk.Panedwindow(root_frame, orient=tk.HORIZONTAL)
        pan.pack(fill=tk.BOTH, expand=True)

        left = ttk.Frame(pan, style="Card.TFrame", padding=10)
        right = ttk.Frame(pan, style="App.TFrame", padding=(5, 0))
        pan.add(left, weight=1)
        pan.add(right, weight=2)

        tabs = ttk.Notebook(right)
        tabs.pack(fill=tk.BOTH, expand=True)

        # --- Aba IA ---
        tab_ia = ttk.Frame(tabs, style="App.TFrame")
        tabs.add(tab_ia, text="🤖 IA Assistente")

        ttk.Label(
            tab_ia,
            text="Pergunte algo ao assistente educacional (dúvidas, estudos, notas, atividades):",
            style="Section.TLabel"
        ).pack(anchor=tk.W, padx=8, pady=(8, 4))

        ia_frame = ttk.Frame(tab_ia, style="Card.TFrame", padding=8)
        ia_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))

        self.ia_log = scrolledtext.ScrolledText(
            ia_frame,
            height=14,
            wrap="word",
            state="disabled",
            font=("Segoe UI", 10),
            background="white"
        )
        self.ia_log.pack(fill=tk.BOTH, expand=True)

        self.ia_log.tag_configure("user", foreground="#0052cc", font=("Segoe UI", 10, "bold"))
        self.ia_log.tag_configure("ia", foreground="#006600", font=("Segoe UI", 10))
        self.ia_log.tag_configure("system", foreground="#999999", font=("Segoe UI", 8, "italic"))

        ia_in = ttk.Frame(tab_ia, style="App.TFrame")
        ia_in.pack(fill=tk.X, padx=8, pady=(0, 10))

        self.ia_entry = ttk.Entry(ia_in)
        self.ia_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        btn_enviar_ia = ttk.Button(ia_in, text="Enviar", style="Accent.TButton", command=self.ia_send)
        btn_enviar_ia.pack(side=tk.LEFT, padx=(6, 0))

        self.ia_entry.bind("<Return>", lambda event: self.ia_send())

        tab_out = ttk.Frame(tabs, style="App.TFrame")
        tabs.add(tab_out, text="📄 Saída / Listagens")

        out_frame = ttk.Frame(tab_out, style="Card.TFrame", padding=8)
        out_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        self.table = ttk.Treeview(out_frame, show="headings")
        self.table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scroll_y = ttk.Scrollbar(out_frame, orient="vertical", command=self.table.yview)
        self.table.configure(yscrollcommand=scroll_y.set)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        if tipo == "admin":
            self._montar_painel_admin(left)
        elif tipo == "professor":
            self._montar_painel_professor(left)
        else:
            self._montar_painel_aluno(left)

    def table_set_columns(self, columns, widths=None):
        """Define colunas da tabela Treeview."""
        self.table.delete(*self.table.get_children())
        self.table["columns"] = columns

        for i, col in enumerate(columns):
            w = widths[i] if widths and i < len(widths) else 120
            self.table.heading(col, text=col)
            self.table.column(col, width=w, anchor="center")

    def table_add_rows(self, rows):
        """Adiciona linhas na tabela."""
        self.table.delete(*self.table.get_children())
        for row in rows:
            self.table.insert("", "end", values=row)

    def _montar_painel_admin(self, frame):
        ttk.Label(frame, text="Painel do Administrador", style="CardTitle.TLabel")\
            .pack(anchor=tk.W, pady=(0, 8))
        ttk.Separator(frame, orient="horizontal").pack(fill="x", pady=(0, 8))
        ttk.Button(frame, text="Cadastrar usuário", command=self.registrar_usuario_prompt).pack(fill=tk.X, pady=4)
        ttk.Button(frame, text="Criar turma", command=self.criar_turma_prompt).pack(fill=tk.X, pady=4)
        ttk.Button(frame, text="Matricular aluno em turma", command=self.matricular_prompt).pack(fill=tk.X, pady=4)
        ttk.Button(frame, text="Lançar nota", command=self.lancar_nota_prompt).pack(fill=tk.X, pady=4)
        ttk.Button(frame, text="Listar alunos de uma turma", command=self.listar_alunos_turma_prompt).pack(fill=tk.X, pady=4)
        ttk.Button(frame, text="Listar turmas", command=self.mostrar_turmas).pack(fill=tk.X, pady=4)
        ttk.Button(frame, text="Criar atividade", command=self.criar_atividade_prompt).pack(fill=tk.X, pady=4)
        ttk.Button(frame, text="Listar atividades", command=self.mostrar_atividades).pack(fill=tk.X, pady=4)

    def _montar_painel_professor(self, frame):
        ttk.Label(frame, text="Painel do Professor", style="CardTitle.TLabel")\
            .pack(anchor=tk.W, pady=(0, 8))
        ttk.Separator(frame, orient="horizontal").pack(fill="x", pady=(0, 8))
        ttk.Button(frame, text="Criar turma", command=self.criar_turma_prompt).pack(fill=tk.X, pady=4)
        ttk.Button(frame, text="Criar atividade", command=self.criar_atividade_prompt).pack(fill=tk.X, pady=4)
        ttk.Button(frame, text="Matricular aluno em MINHA turma", command=self.matricular_prompt).pack(fill=tk.X, pady=4)
        ttk.Button(frame, text="Lançar nota", command=self.lancar_nota_prompt).pack(fill=tk.X, pady=4)
        ttk.Button(frame, text="Listar alunos de minha turma", command=self.listar_alunos_turma_prompt).pack(fill=tk.X, pady=4)
        ttk.Button(frame, text="Listar minhas turmas", command=self.mostrar_turmas).pack(fill=tk.X, pady=4)
        ttk.Button(frame, text="Listar atividades", command=self.mostrar_atividades).pack(fill=tk.X, pady=4)

    def _montar_painel_aluno(self, frame):
        ttk.Label(frame, text="Painel do Aluno", style="CardTitle.TLabel")\
            .pack(anchor=tk.W, pady=(0, 8))
        ttk.Separator(frame, orient="horizontal").pack(fill="x", pady=(0, 8))
        ttk.Button(frame, text="Listar MINHAS turmas", command=self.listar_minhas_turmas).pack(fill=tk.X, pady=4)
        ttk.Button(frame, text="Listar atividades", command=self.mostrar_atividades).pack(fill=tk.X, pady=4)
        ttk.Button(frame, text="Entregar atividade", command=self.entregar_atividade_prompt).pack(fill=tk.X, pady=4)
        ttk.Button(frame, text="Ver minhas notas", command=self.ver_notas).pack(fill=tk.X, pady=4)
        ttk.Button(frame, text="Ver meu boletim", command=self.ver_boletim).pack(fill=tk.X, pady=4)
    # ---------- IA  ----------
    def ia_send(self):
        pergunta = self.ia_entry.get().strip()
        if not pergunta:
            return
        
        self.ia_log.config(state="normal")
        self.ia_log.insert(tk.END, f"Você: {pergunta}\n", "user")

        resp = ia_responder(pergunta)

        self.ia_log.insert(tk.END, f"IA: {resp}\n\n", "ia")
        self.ia_log.config(state="disabled")

        self.ia_entry.delete(0, tk.END)
        self.ia_log.see(tk.END)

    def logout(self):
        self.current_user = None
        self.root.geometry("")
        self.build_login()

    def criar_turma_prompt(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Criar turma")
        dialog.geometry("520x360")
        for i in range(2):
            dialog.columnconfigure(i, weight=1)

        login_atual, tipo_atual = self.current_user

        # Campos básicos
        campos = ["ID (ex: T01)", "Nome", "Descrição", "Capacidade (nº)", "Qtd atividades (bimestre)"]
        entradas = []
        for i, c in enumerate(campos):
            ttk.Label(dialog, text=c + ":").grid(row=i, column=0, sticky=tk.E, pady=3)
            e = ttk.Entry(dialog)
            e.grid(row=i, column=1, sticky="ew", pady=3)
            entradas.append(e)

        entry_prof = None
        if tipo_atual == "admin":
            ttk.Label(dialog, text="Login do professor responsável:").grid(
                row=len(campos), column=0, sticky=tk.E, pady=3
            )
            entry_prof = ttk.Entry(dialog)
            entry_prof.grid(row=len(campos), column=1, sticky="ew", pady=3)

        def criar():
            idv, nome, desc, cap, qtd = [e.get().strip() for e in entradas]

            if not idv or not nome or not cap.isdigit() or not qtd.isdigit():
                messagebox.showerror(
                    "Erro",
                    "ID, Nome, Capacidade e Qtd. atividades são obrigatórios (números)."
             )
                return

            if tipo_atual == "admin":
                prof_login = (entry_prof.get().strip() if entry_prof else "")
                if not prof_login:
                    messagebox.showerror("Erro", "Informe o login do professor responsável.")
                    return
            else:
                prof_login = login_atual

            ok, msg = criar_turma_c(idv, nome, desc, prof_login, int(cap))

            if ok:
                if not salvar_turma_qtd_atividades_c(idv, int(qtd)):
                    messagebox.showwarning(
                        "Aviso",
                        "Turma criada, mas não consegui salvar a Qtd. de atividades do bimestre."
                    )
            messagebox.showinfo("Resultado", msg)
            if ok:
                dialog.destroy()

        linha_botao = len(campos) + (1 if tipo_atual == "admin" else 0)
        ttk.Button(dialog, text="Criar", command=criar).grid(
            row=linha_botao, column=0, columnspan=2, pady=8
        )


    def matricular_prompt(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Matricular aluno em MINHA turma")
        dialog.geometry("520x220")
        for i in range(2):
            dialog.columnconfigure(i, weight=1)

        # Campos
        ttk.Label(dialog, text="Turma ID (ex: T01):").grid(row=0, column=0, sticky=tk.E, pady=4)
        e_turma = ttk.Entry(dialog); e_turma.grid(row=0, column=1, sticky="ew", pady=4)
        ttk.Label(dialog, text="Login do aluno:").grid(row=1, column=0, sticky=tk.E, pady=4)
        e_aluno = ttk.Entry(dialog); e_aluno.grid(row=1, column=1, sticky="ew", pady=4)

        def acao():
            turma_id = e_turma.get().strip()
            aluno_login = e_aluno.get().strip()
            if not turma_id or not aluno_login:
                messagebox.showerror("Erro", "Informe Turma ID e Login do aluno.")
                return

            actor = self.current_user[0]

        # Tenta chamar o wrapper que você tiver (matricular_aluno_c é o nome mais comum)
            try:
                ok, msg = matricular_aluno_c(turma_id, aluno_login, actor)
            except Exception as ex:
                messagebox.showerror("Erro", f"Falha ao chamar matrícula: {ex}")
                return

            messagebox.showinfo("Resultado", msg)
            if ok:
                dialog.destroy()

        ttk.Button(dialog, text="Matricular", command=acao).grid(row=2, column=0, columnspan=2, pady=8)


    def lancar_nota_prompt(self):
        dialog = tk.Toplevel(self.root); dialog.title("Lançar nota"); dialog.geometry("560x300")
        for i in range(2): dialog.columnconfigure(i, weight=1)
        campos = ["Turma ID", "Login do aluno", "Disciplina", "Nota (0-10)", "Código da folha"]
        entradas=[]
        for i,c in enumerate(campos):
            ttk.Label(dialog, text=c+":").grid(row=i, column=0, sticky=tk.E, pady=3)
            e=ttk.Entry(dialog); e.grid(row=i, column=1, sticky="ew", pady=3); entradas.append(e)

        def _append_nota_meta(aluno_login, turma_id, disciplina, cod_folha, nota):
            try:
                path = os.path.join(os.getcwd(), "notas_meta.txt")
                with open(path, "a", encoding="utf-8") as f:
                    f.write(f"{aluno_login};{turma_id};{disciplina};{cod_folha or '-'};{nota}\n")
                return True
            except Exception:
                return False

        def acao():
            turma, aluno, disc, nota, cod_folha = [e.get().strip() for e in entradas]
            actor = self.current_user[0]
            ok,msg = lancar_nota_c(turma, aluno, disc, nota, actor)
            if ok:
                if not _append_nota_meta(aluno, turma, disc, cod_folha, nota):
                    messagebox.showwarning("Aviso", "Nota lançada, mas não consegui salvar o Código da folha em notas_meta.txt.")
            messagebox.showinfo("Resultado", msg)
            if ok: dialog.destroy()
        ttk.Button(dialog, text="Lançar", command=acao).grid(row=len(campos), column=0, columnspan=2, pady=8)
    def criar_atividade_prompt(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Criar atividade")
        dialog.geometry("560x360")
        for i in range(2):
            dialog.columnconfigure(i, weight=1)

        campos = [
            "ID (A01)",
            "Turma ID",
            "Título",
            "Descrição",
            "Prazo (YYYY-MM-DD)",
            "Código da folha",
            "Data de lançamento (YYYY-MM-DD)"
        ]
        entradas = []
        for i, campo in enumerate(campos):
            ttk.Label(dialog, text=campo + ":").grid(row=i, column=0, sticky=tk.E, pady=3)
            e = ttk.Entry(dialog)
            e.grid(row=i, column=1, sticky="ew", pady=3)
            entradas.append(e)

        def criar():
            idv, turma, titulo, desc, prazo, cod_folha, data_lanc = [e.get().strip() for e in entradas]
            if not idv or not turma or not titulo:
                messagebox.showerror("Erro", "ID, Turma ID e Título são obrigatórios.")
                return
            autor = self.current_user[0]
            ok, msg = criar_atividade_c(idv, turma, titulo, desc, prazo, autor)
            if ok:
                # salva meta: código da folha e data de lançamento no backend
                try:
                    salvar_meta_atividade_c(idv, cod_folha or "-", data_lanc or "-")
                except Exception:
                    pass
            messagebox.showinfo("Resultado", msg)
            if ok:
                dialog.destroy()

        ttk.Button(dialog, text="Criar", command=criar).grid(row=len(campos), column=0, columnspan=2, pady=8)

    def listar_alunos_turma_prompt(self):
        turma = simpledialog.askstring("Listar alunos", "Turma ID:", parent=self.root)
        if not turma:
            return

        texto = listar_alunos_turma_c(turma.strip())
        linhas = [l.strip() for l in texto.splitlines() if l.strip()]

        if not linhas or "nenhum" in linhas[0].lower():
            self.table_set_columns(["Mensagem"])
            self.table_add_rows([[f"Nenhum aluno encontrado na turma {turma}."]])
            return

        self.table_set_columns(["Login"], [180])
        rows = [[aluno] for aluno in linhas]
        self.table_add_rows(rows)

    def mostrar_turmas(self):
        texto = listar_turmas_c()
        linhas = [l.strip() for l in texto.splitlines() if l.strip()]

        if not linhas or linhas[0].lower().startswith("nenhuma"):
            self.table_set_columns(["Mensagem"])
            self.table_add_rows([["Nenhuma turma cadastrada."]])
            return

        cols = ["ID", "Nome", "Descrição", "Professor", "Capacidade"]
        self.table_set_columns(cols, [60, 160, 220, 120, 80])

        rows = []
        for linha in linhas:
            partes = linha.split(";")
            if len(partes) >= 5:
                rows.append(partes[:5])

        self.table_add_rows(rows)

    def entregar_atividade_prompt(self):
        dialog = tk.Toplevel(self.root); dialog.title("Entregar atividade"); dialog.geometry("480x240")
        for i in range(2): dialog.columnconfigure(i, weight=1)
        labels = ["ID da atividade (ex: A01)", "Código da folha", "Data de lançamento (YYYY-MM-DD)"]
        entradas=[]
        for i, lab in enumerate(labels):
            ttk.Label(dialog, text=lab+":").grid(row=i, column=0, sticky=tk.E, pady=3)
            e = ttk.Entry(dialog); e.grid(row=i, column=1, sticky="ew", pady=3); entradas.append(e)
        def acao():
            atividade_id, cod_folha, data_lanc = [e.get().strip() for e in entradas]
            if not atividade_id: return
            login = self.current_user[0]
            ok, msg = entregar_atividade_c(atividade_id.strip(), login)
            if ok:
                if not registrar_entrega_meta_c(atividade_id.strip(), login, cod_folha or "-", data_lanc or "-"):
                    messagebox.showwarning("Aviso", "Entrega registrada, mas não consegui salvar Código/Data da folha.")
            messagebox.showinfo("Resultado", msg)
            if ok: dialog.destroy()
        ttk.Button(dialog, text="Entregar", command=acao).grid(row=len(labels), column=0, columnspan=2, pady=8)
    def mostrar_atividades(self):
        texto = listar_atividades_c()
        linhas = [l.strip() for l in texto.splitlines() if l.strip()]

        if not linhas or linhas[0].lower().startswith("nenhuma"):
            self.table_set_columns(["Mensagem"])
            self.table_add_rows([["Nenhuma atividade cadastrada."]])
            return

        login, tipo = self.current_user  
        turmas_permitidas = None
        if tipo == "aluno":
            turmas_permitidas = _turmas_do_aluno(login)

        # carrega meta
        meta = {}
        try:
            p = os.path.join(os.getcwd(), "atividades_meta.txt")
            if os.path.exists(p):
                with open(p,"r",encoding="utf-8",errors="ignore") as f:
                    for ln in f:
                        a = ln.strip().split(";")
                        if len(a)>=3:
                            meta[a[0]] = (a[1], a[2]) 
        except:
            pass

        cols = ["ID", "Turma", "Título", "Cód.Folha", "Lançamento", "Prazo", "Autor"]
        self.table_set_columns(cols, [60, 60, 160, 100, 100, 100, 120])

        rows = []
        for linha in linhas:
            partes = linha.split(";")
            if len(partes) >= 6:
                id_, turma, tit, desc, prazo, autor = partes[:6]
                if turmas_permitidas and turma not in turmas_permitidas:
                    continue
                cod, dat = meta.get(id_, ("-", "-"))
                rows.append([id_, turma, tit[:20], cod, dat, prazo, autor])

        if not rows:
            self.table_set_columns(["Mensagem"])
            self.table_add_rows([["Você ainda não tem atividades nas suas turmas."]])
            return

        self.table_add_rows(rows)

    def listar_minhas_turmas(self):
        aluno = self.current_user[0]
        texto = listar_turmas_do_aluno_c(aluno)
        linhas = [l.strip() for l in texto.splitlines() if l.strip()]

        if not linhas:
            self.table_set_columns(["Mensagem"])
            self.table_add_rows([["Nenhuma turma encontrada."]])
            return

        self.table_set_columns(["Turmas"], [200])
        self.table_add_rows([[l] for l in linhas])

    def ver_notas(self):
        aluno = self.current_user[0]
        texto = consultar_notas_c(aluno)
        linhas = [l.strip() for l in texto.splitlines() if l.strip()]

        if not linhas or "sem notas" in linhas[0].lower():
            self.table_set_columns(["Mensagem"])
            self.table_add_rows([["Nenhuma nota lançada ainda."]])
            return

        cols = ["Turma", "Disciplina", "Nota"]
        self.table_set_columns(cols, [80, 200, 60])

        rows = []
        for linha in linhas:
            if "|" in linha:
                partes = [p.strip() for p in linha.split("|")]
                turma = partes[0].split(":")[1].strip()
                disc = partes[1].split(":")[1].strip()
                nota = partes[2].split(":")[1].strip()
                rows.append([turma, disc, nota])

        self.table_add_rows(rows)

    def ver_boletim(self):
        aluno = self.current_user[0]
        texto = boletim_c(aluno)

        if not texto or texto.lower().startswith("sem notas"):
            self.table_set_columns(["Mensagem"])
            self.table_add_rows([["Nenhum boletim disponível."]])
            return

        linhas = [l.strip() for l in texto.splitlines() if l.strip()]
        cols = ["Informações"]
        self.table_set_columns(cols, [400])

        rows = [[linha] for linha in linhas]
        self.table_add_rows(rows)

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
