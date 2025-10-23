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

# ==== Wrappers ====
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
            model="gpt-4o-mini",  # rápido + barato — pode trocar por gpt-4.1 se quiser
            messages=[
                {"role": "system", "content": "Você é um assistente educacional dentro do sistema EduConnect. Responda de forma clara e breve."},
                {"role": "user", "content": pergunta}
            ],
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"Erro na IA: {e}"
    
class App:
    def __init__(self, root):
        self.root = root
        root.title("EduConnect - Sistema Acadêmico (PIM)")
        root.geometry("1024x720")
        root.minsize(800, 600)
        root.rowconfigure(0, weight=1)
        root.columnconfigure(0, weight=1)

        default_font = tkfont.nametofont("TkDefaultFont")
        default_font.configure(size=11)

        self.current_user = None  # (login, tipo)
        self.build_login()

    # ---------- LOGIN ----------
    def build_login(self):
        for w in self.root.winfo_children():
            w.destroy()

        frame = ttk.Frame(self.root, padding=12)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="EduConnect - Login", font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=10)

        ttk.Label(frame, text="Login:").grid(row=1, column=0, sticky=tk.E)
        self.login_entry = ttk.Entry(frame)
        self.login_entry.grid(row=1, column=1, sticky="ew")

        ttk.Label(frame, text="Senha:").grid(row=2, column=0, sticky=tk.E)
        self.senha_entry = ttk.Entry(frame, show="*")
        self.senha_entry.grid(row=2, column=1, sticky="ew")

        frame.columnconfigure(1, weight=1)

        ttk.Button(frame, text="Entrar", command=self.tentar_login).grid(row=3, column=0, pady=8)
        ttk.Button(frame, text="Registrar (admin apenas)", command=self.registrar_usuario_prompt).grid(row=3, column=1, pady=8)

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

        frame = ttk.Frame(self.root, padding=8)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text=f"Bem-vindo: {login} ({tipo})", font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=(0, 8))

        pan = ttk.Panedwindow(frame, orient=tk.HORIZONTAL)
        pan.pack(fill=tk.BOTH, expand=True)

        left = ttk.Frame(pan)
        right = ttk.Frame(pan)
        pan.add(left, weight=1)
        pan.add(right, weight=2)
        tabs = ttk.Notebook(right)
        tabs.pack(fill=tk.BOTH, expand=True)

        # --- Aba IA ---
        tab_ia = ttk.Frame(tabs)
        tabs.add(tab_ia, text="🤖 IA Assistente")

        ttk.Label(tab_ia, text="Pergunte algo à IA (dicas, dúvidas, explicações):").pack(anchor=tk.W, padx=6, pady=(6,2))
        ia_frame = ttk.Frame(tab_ia)
        ia_frame.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        self.ia_log = scrolledtext.ScrolledText(ia_frame, height=12)
        self.ia_log.pack(fill=tk.BOTH, expand=True)
        ia_in = ttk.Frame(tab_ia)
        ia_in.pack(fill=tk.X, padx=6, pady=(0,8))
        self.ia_entry = ttk.Entry(ia_in)
        self.ia_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(ia_in, text="Enviar", command=self.ia_send).pack(side=tk.LEFT, padx=(6,0))

        # --- Aba Saída ---
        tab_out = ttk.Frame(tabs)
        tabs.add(tab_out, text="📄 Saída / Listagens")

        self.output = scrolledtext.ScrolledText(tab_out)
        self.output.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        if tipo == "admin":
            self._montar_painel_admin(left)
        elif tipo == "professor":
            self._montar_painel_professor(left)
        else:
            self._montar_painel_aluno(left)

        # Chat/Output (simples)
        ttk.Label(right, text="Saída / Listagem").pack(anchor=tk.W, pady=(8, 0))
        self.output = scrolledtext.ScrolledText(right)
        self.output.pack(fill=tk.BOTH, expand=True)

    def _montar_painel_admin(self, frame):
        ttk.Label(frame, text="Painel Administrador").pack(anchor=tk.W)
        ttk.Button(frame, text="Cadastrar usuário", command=self.registrar_usuario_prompt).pack(fill=tk.X, pady=4)
        ttk.Button(frame, text="Criar turma", command=self.criar_turma_prompt).pack(fill=tk.X, pady=4)
        ttk.Button(frame, text="Matricular aluno em turma", command=self.matricular_prompt).pack(fill=tk.X, pady=4)
        ttk.Button(frame, text="Lançar nota", command=self.lancar_nota_prompt).pack(fill=tk.X, pady=4)
        ttk.Button(frame, text="Listar alunos de uma turma", command=self.listar_alunos_turma_prompt).pack(fill=tk.X, pady=4)
        ttk.Button(frame, text="Listar turmas", command=self.mostrar_turmas).pack(fill=tk.X, pady=4)
        ttk.Button(frame, text="Criar atividade", command=self.criar_atividade_prompt).pack(fill=tk.X, pady=4)
        ttk.Button(frame, text="Listar atividades", command=self.mostrar_atividades).pack(fill=tk.X, pady=4)

    def _montar_painel_professor(self, frame):
        ttk.Label(frame, text="Painel Professor").pack(anchor=tk.W)
        ttk.Button(frame, text="Criar turma", command=self.criar_turma_prompt).pack(fill=tk.X, pady=4)
        ttk.Button(frame, text="Criar atividade", command=self.criar_atividade_prompt).pack(fill=tk.X, pady=4)
        ttk.Button(frame, text="Matricular aluno em MINHA turma", command=self.matricular_prompt).pack(fill=tk.X, pady=4)
        ttk.Button(frame, text="Lançar nota", command=self.lancar_nota_prompt).pack(fill=tk.X, pady=4)
        ttk.Button(frame, text="Listar alunos de minha turma", command=self.listar_alunos_turma_prompt).pack(fill=tk.X, pady=4)
        ttk.Button(frame, text="Listar minhas turmas", command=self.mostrar_turmas).pack(fill=tk.X, pady=4)
        ttk.Button(frame, text="Listar atividades", command=self.mostrar_atividades).pack(fill=tk.X, pady=4)

    def _montar_painel_aluno(self, frame):
        ttk.Label(frame, text="Painel Aluno").pack(anchor=tk.W)
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
        self.ia_log.insert(tk.END, f"Você: {pergunta}\n")
        resp = ia_responder(pergunta)
        self.ia_log.insert(tk.END, f"IA: {resp}\n\n")
        self.ia_entry.delete(0, tk.END)
        self.ia_log.see(tk.END)
    # ---------- Ações / Diálogos ----------
    def logout(self):
        self.current_user = None
        self.root.geometry("")
        self.build_login()

    def criar_turma_prompt(self):
        dialog = tk.Toplevel(self.root); dialog.title("Criar turma"); dialog.geometry("420x280")
        for i in range(2): dialog.columnconfigure(i, weight=1)
        campos = ["ID (ex: T01)", "Nome", "Descrição", "Capacidade (nº)"]
        entradas=[]
        for i,c in enumerate(campos):
            ttk.Label(dialog, text=c+":").grid(row=i, column=0, sticky=tk.E, pady=3)
            e=ttk.Entry(dialog); e.grid(row=i, column=1, sticky="ew", pady=3); entradas.append(e)
        def criar():
            idv, nome, desc, cap = [e.get().strip() for e in entradas]
            if not idv or not nome or not cap.isdigit():
                messagebox.showerror("Erro", "ID, Nome e Capacidade numérica são obrigatórios."); return
            actor = self.current_user[0]
            ok,msg = criar_turma_c(idv, nome, desc, actor, int(cap))
            messagebox.showinfo("Resultado", msg); 
            if ok: dialog.destroy()
        ttk.Button(dialog, text="Criar", command=criar).grid(row=4, column=0, columnspan=2, pady=8)

    def matricular_prompt(self):
        dialog = tk.Toplevel(self.root); dialog.title("Matricular aluno"); dialog.geometry("420x220")
        for i in range(2): dialog.columnconfigure(i, weight=1)
        campos = ["Turma ID", "Login do aluno"]
        entradas=[]
        for i,c in enumerate(campos):
            ttk.Label(dialog, text=c+":").grid(row=i, column=0, sticky=tk.E, pady=3)
            e=ttk.Entry(dialog); e.grid(row=i, column=1, sticky="ew", pady=3); entradas.append(e)
        def acao():
            turma, aluno = [e.get().strip() for e in entradas]
            actor = self.current_user[0]
            ok,msg = matricular_aluno_c(turma, aluno, actor)
            messagebox.showinfo("Resultado", msg)
            if ok: dialog.destroy()
        ttk.Button(dialog, text="Matricular", command=acao).grid(row=2, column=0, columnspan=2, pady=8)

    def lancar_nota_prompt(self):
        dialog = tk.Toplevel(self.root); dialog.title("Lançar nota"); dialog.geometry("480x260")
        for i in range(2): dialog.columnconfigure(i, weight=1)
        campos = ["Turma ID", "Login do aluno", "Disciplina", "Nota (0-10)"]
        entradas=[]
        for i,c in enumerate(campos):
            ttk.Label(dialog, text=c+":").grid(row=i, column=0, sticky=tk.E, pady=3)
            e=ttk.Entry(dialog); e.grid(row=i, column=1, sticky="ew", pady=3); entradas.append(e)
        def acao():
            turma, aluno, disc, nota = [e.get().strip() for e in entradas]
            actor = self.current_user[0]
            ok,msg = lancar_nota_c(turma, aluno, disc, nota, actor)
            messagebox.showinfo("Resultado", msg)
            if ok: dialog.destroy()
        ttk.Button(dialog, text="Lançar", command=acao).grid(row=4, column=0, columnspan=2, pady=8)

    def listar_alunos_turma_prompt(self):
        turma = simpledialog.askstring("Listar alunos", "Turma ID:", parent=self.root)
        if not turma:
            return
        texto = listar_alunos_turma_c(turma.strip())
        linhas = [l.strip() for l in texto.splitlines() if l.strip()]
        if not linhas or "nenhum" in linhas[0].lower():
            saida = f"👥 Nenhum aluno encontrado na turma {turma}."
        else:
            saida = f"👩‍🎓 ALUNOS DA TURMA {turma}\n\n"
            saida += f"{'LOGIN':<25}\n"
            saida += "-" * 25 + "\n"
            for aluno in linhas:
                saida += f"{aluno:<25}\n"
        self.output.delete("1.0", tk.END)
        self.output.insert(tk.END, saida)

    def mostrar_turmas(self):
        texto = listar_turmas_c()
        linhas = [l.strip() for l in texto.splitlines() if l.strip()]
        if not linhas or linhas[0].lower().startswith("nenhuma"):
            saida = "📚 Nenhuma turma cadastrada."
        else:
            saida = "📘 TURMAS CADASTRADAS\n\n"
            saida += f"{'ID':<8} {'NOME':<25} {'DESCRIÇÃO':<30} {'PROFESSOR':<15} {'CAPACIDADE':<10}\n"
            saida += "-" * 90 + "\n"
            for linha in linhas:
                partes = linha.split(";")
                if len(partes) >= 5:
                    id_, nome, desc, prof, cap = partes[:5]
                    saida += f"{id_:<8} {nome:<25} {desc:<30} {prof:<15} {cap:<10}\n"
        self.output.delete("1.0", tk.END)
        self.output.insert(tk.END, saida)

    def criar_atividade_prompt(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Criar atividade")
        dialog.geometry("480x320")
        for i in range(2):
            dialog.columnconfigure(i, weight=1)

        campos = ["ID (A01)", "Turma ID", "Título", "Descrição", "Prazo"]
        entradas = []

        for i, campo in enumerate(campos):
            ttk.Label(dialog, text=campo + ":").grid(row=i, column=0, sticky=tk.E, pady=3)
            e = ttk.Entry(dialog)
            e.grid(row=i, column=1, sticky="ew", pady=3)
            entradas.append(e)

        def criar():
            idv, turma, titulo, desc, prazo = [e.get().strip() for e in entradas]
            if not idv or not turma or not titulo:
                messagebox.showerror("Erro", "ID, Turma ID e Título são obrigatórios.")
                return
            autor = self.current_user[0]
            ok, msg = criar_atividade_c(idv, turma, titulo, desc, prazo, autor)
            messagebox.showinfo("Resultado", msg)
            if ok:
                dialog.destroy()

        ttk.Button(dialog, text="Criar", command=criar).grid(row=5, column=0, columnspan=2, pady=8)

    def mostrar_atividades(self):
        texto = listar_atividades_c()
        linhas = [l.strip() for l in texto.splitlines() if l.strip()]
        if not linhas or linhas[0].lower().startswith("nenhuma"):
            saida = "📝 Nenhuma atividade cadastrada."
        else:
            saida = "🧾 ATIVIDADES CADASTRADAS\n\n"
            saida += f"{'ID':<6} {'TURMA':<8} {'TÍTULO':<25} {'DESCRIÇÃO':<30} {'PRAZO':<15} {'AUTOR':<15}\n"
            saida += "-" * 110 + "\n"
            for linha in linhas:
                partes = linha.split(";")
                if len(partes) >= 6:
                    id_, turma, titulo, desc, prazo, autor = partes[:6]
                    saida += f"{id_:<6} {turma:<8} {titulo:<25} {desc:<30} {prazo:<15} {autor:<15}\n"
        self.output.delete("1.0", tk.END)
        self.output.insert(tk.END, saida)


    def entregar_atividade_prompt(self):
        atividade_id = simpledialog.askstring("Entregar", "ID da atividade (ex: A01):", parent=self.root)
        if not atividade_id:
            return
        login = self.current_user[0]
        ok, msg = entregar_atividade_c(atividade_id.strip(), login)
        messagebox.showinfo("Resultado", msg)

    def listar_minhas_turmas(self):
        aluno = self.current_user[0]
        texto = listar_turmas_do_aluno_c(aluno)
        self.output.delete("1.0", tk.END); self.output.insert(tk.END, texto)

    def ver_notas(self):
        aluno = self.current_user[0]
        texto = consultar_notas_c(aluno)
        linhas = [l.strip() for l in texto.splitlines() if l.strip()]
        if not linhas or "sem notas" in linhas[0].lower():
            saida = "🎯 Nenhuma nota lançada ainda."
        else:
            saida = "📖 MINHAS NOTAS\n\n"
            saida += f"{'TURMA':<10} {'DISCIPLINA':<25} {'NOTA':<5}\n"
            saida += "-" * 45 + "\n"
            for linha in linhas:
                if "|" in linha:
                    partes = [p.strip() for p in linha.split("|")]
                    if len(partes) >= 3:
                        turma = partes[0].split(":")[1].strip()
                        disc = partes[1].split(":")[1].strip()
                        nota = partes[2].split(":")[1].strip()
                        saida += f"{turma:<10} {disc:<25} {nota:<5}\n"
        self.output.delete("1.0", tk.END)
        self.output.insert(tk.END, saida)

    def ver_boletim(self):
        aluno = self.current_user[0]
        texto = boletim_c(aluno)
        linhas = [l.strip() for l in texto.splitlines() if l.strip()]
        if not linhas or linhas[0].lower().startswith("sem notas"):
            saida = "📚 Nenhum boletim disponível."
            self.output.delete("1.0", tk.END); self.output.insert(tk.END, saida); return

        # Ex.: "Disciplina:Matemática | Média:8.50 (3 lançamentos)"
        padrao = re.compile(r"Disciplina:(?P<disc>.*?)\s*\|\s*M[ée]dia:(?P<media>[0-9]+(?:\.[0-9]+)?)\s*\((?P<qtd>\d+)\s+lan", re.IGNORECASE)

        registros = []
        for ln in linhas:
            m = padrao.search(ln)
            if m:
                registros.append( (m.group("disc").strip(), m.group("media").strip(), m.group("qtd").strip()) )

        if not registros:
            # Fallback: mostra o texto bruto se não deu match (para não “sumir” com nada)
            saida = "🏆 BOLETIM (formato inesperado — mostrando texto original)\n\n" + texto
        else:
            saida = "🏆 BOLETIM FINAL\n\n"
            saida += f"{'DISCIPLINA':<28} {'MÉDIA':<8} {'LANÇAMENTOS':<12}\n"
            saida += "-" * 54 + "\n"
            for disc, media, qtd in registros:
                saida += f"{disc:<28} {media:<8} {qtd:<12}\n"

        self.output.delete("1.0", tk.END)
        self.output.insert(tk.END, saida)

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
