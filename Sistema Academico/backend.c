#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#if defined(_WIN32) || defined(_WIN64)
    #define EXPORT __declspec(dllexport)
#else
    #define EXPORT
#endif

static void trim(char *s){
    if (!s) return;
    size_t len = strlen(s);
    while (len > 0 && (s[len-1] == '\r' || s[len-1] == '\n' || s[len-1] == ' ' || s[len-1] == '\t')){
        s[--len] = '\0';
    }
}

/* =========================
   Utilidades e Inicialização
   ========================= */

static void ensure_file(const char *path){
    FILE *f = fopen(path, "a");
    if (f) fclose(f);
}

static void ensure_meta_files(){
    ensure_file("atividades_meta.txt");
    ensure_file("turmas_meta.txt");
    ensure_file("entregas_meta.txt");
    ensure_file("notas_meta.txt");
}

EXPORT void inicializar_arquivos(){
    ensure_file("usuarios.txt");     /* login;nome;senha;tipo */
    ensure_file("turmas.txt");       /* id;nome;descricao;prof_login;capacidade_int */
    ensure_file("atividades.txt");   /* id;turma_id;titulo;descricao;prazo;autor_login;entregues_csv */
    ensure_file("matriculas.txt");   /* turma_id;aluno_login */
    ensure_file("notas.txt");        /* aluno_login;turma_id;disciplina;nota */
    ensure_meta_files();
}

/* =========================
   Usuários e Autenticação
   ========================= */

EXPORT int salvar_usuario(const char* login, const char* nome, const char* senha, const char* tipo){
    if (!login || !nome || !senha || !tipo) return 2;

    FILE *f = fopen("usuarios.txt", "r");
    if (f){
        char line[512];
        while (fgets(line, sizeof(line), f)){
            char lgin[100], nm[100], pass[100], t[50];
            if (sscanf(line, "%99[^;];%99[^;];%99[^;];%49[^\n]", lgin, nm, pass, t)==4){
                if (strcmp(lgin, login)==0){ fclose(f); return 1; }
            }
        }
        fclose(f);
    }
    f = fopen("usuarios.txt", "a");
    if (!f) return 2;
    fprintf(f, "%s;%s;%s;%s\n", login, nome, senha, tipo);
    fclose(f);
    return 0;
}
EXPORT int salvar_meta_atividade(const char* atividade_id,
                                 const char* codigo_folha,
                                 const char* data_lanc){
    if (!atividade_id) return 2;
    ensure_meta_files();
    
    FILE *fin = fopen("atividades_meta.txt","r");
    FILE *fout = fopen("atividades_meta.new","w");
    if (!fout) { if (fin) fclose(fin); return 2; }
    char line[512]; int found = 0;
    if (fin){
        while (fgets(line,sizeof(line),fin)){
            char id[120], cod[120], dt[120];
            int n = sscanf(line,"%119[^;];%119[^;];%119[^\n]", id,cod,dt);
            if (n>=1 && strcmp(id,atividade_id)==0){
                fprintf(fout, "%s;%s;%s\n", atividade_id, codigo_folha?codigo_folha:"-", data_lanc?data_lanc:"-");
                found = 1;
            } else {
                fputs(line, fout);
            }
        }
        fclose(fin);
    }
    if (!found){
        fprintf(fout, "%s;%s;%s\n", atividade_id, codigo_folha?codigo_folha:"-", data_lanc?data_lanc:"-");
    }
    fclose(fout);
    remove("atividades_meta.txt");
    rename("atividades_meta.new","atividades_meta.txt");
    return 0;
}

EXPORT int registrar_entrega_meta(const char* atividade_id,
                                  const char* aluno_login,
                                  const char* codigo_folha,
                                  const char* data_lanc){
    if (!atividade_id || !aluno_login) return 2;
    ensure_meta_files();
    FILE *f = fopen("entregas_meta.txt","a");
    if (!f) return 2;
    fprintf(f, "%s;%s;%s;%s\n", atividade_id, aluno_login,
            codigo_folha?codigo_folha:"-", data_lanc?data_lanc:"-");
    fclose(f);
    return 0;
}

EXPORT int salvar_turma_qtd_atividades(const char* turma_id, int qtd){
    if (!turma_id || qtd < 0) return 2;
    ensure_meta_files();
    FILE *fin = fopen("turmas_meta.txt","r");
    FILE *fout = fopen("turmas_meta.new","w");
    if (!fout){ if (fin) fclose(fin); return 2; }
    char line[256]; int found = 0;
    if (fin){
        while (fgets(line,sizeof(line),fin)){
            char tid[120]; int q=0;
            if (sscanf(line,"%119[^;];%d", tid,&q)==2){
                if (strcmp(tid,turma_id)==0){
                    fprintf(fout, "%s;%d\n", turma_id, qtd);
                    found = 1;
                } else fputs(line,fout);
            }
        }
        fclose(fin);
    }
    if (!found) fprintf(fout, "%s;%d\n", turma_id, qtd);
    fclose(fout);
    remove("turmas_meta.txt");
    rename("turmas_meta.new","turmas_meta.txt");
    return 0;
}

EXPORT int autenticar(const char* login, const char* senha_informada, char* buffer_tipo, int buffer_tamanho){
    if (!login || !senha_informada || !buffer_tipo || buffer_tamanho<=1) return 3;
    FILE *f = fopen("usuarios.txt","r");
    if (!f) return 3;
    char line[512];
    while (fgets(line, sizeof(line), f)){
        char lgin[100], nome[100], senha_lida[100], tipo[50];
         if (sscanf(line, "%99[^;];%99[^;];%99[^;];%49[^\n]", lgin, nome, senha_lida, tipo)==4){
            if (strcmp(lgin, login)==0){
                if (strcmp(senha_lida, senha_informada)==0){
                    trim(tipo);  
                    strncpy(buffer_tipo, tipo, buffer_tamanho-1);
                    buffer_tipo[buffer_tamanho-1]='\0';
                    fclose(f);
                    return 0;
                } else {
                    fclose(f);
                    return 2;
                }
            }
        }
    }
    fclose(f);
    return 1;
}

/* =========================
   Helpers RBAC / Turmas
   ========================= */

static int buscar_tipo_usuario(const char* login, char* tipo_out, int tipo_out_sz){
    if (!login) return 0;
    FILE *f = fopen("usuarios.txt","r");
    if (!f) return 0;
    char line[512];
    int ok=0;
    while (fgets(line,sizeof(line),f)){
        char lgin[100], nome[100], senha[100], tipo[50];
        if (sscanf(line,"%99[^;];%99[^;];%99[^;];%49[^\n]", lgin,nome,senha,tipo)==4){
            if (strcmp(lgin,login)==0){
                trim(tipo); 
                if (tipo_out && tipo_out_sz>0){
                    strncpy(tipo_out, tipo, tipo_out_sz-1);
                    tipo_out[tipo_out_sz-1]='\0';
                }
                ok=1;
                break;
            }
        }
    }
    fclose(f);
    return ok;
}

static int eh_admin(const char* login){
    char t[50]; return buscar_tipo_usuario(login,t,sizeof(t)) && strcmp(t,"admin")==0;
}
static int eh_professor(const char* login){
    char t[50]; return buscar_tipo_usuario(login,t,sizeof(t)) && strcmp(t,"professor")==0;
}
static int eh_aluno(const char* login){
    char t[50]; return buscar_tipo_usuario(login,t,sizeof(t)) && strcmp(t,"aluno")==0;
}

static int professor_da_turma(const char* login, const char* turma_id){
    if (!login || !turma_id) return 0;
    FILE *f = fopen("turmas.txt","r");
    if (!f) return 0;
    char line[512];
    int ok=0;
    while (fgets(line,sizeof(line),f)){
        char id[100], nome[100], desc[200], prof[100];
        int cap=0;
        if (sscanf(line,"%99[^;];%99[^;];%199[^;];%99[^;];%d", id,nome,desc,prof,&cap)>=5){
            if (strcmp(id,turma_id)==0 && strcmp(prof,login)==0){ ok=1; break; }
        }
    }
    fclose(f);
    return ok;
}

static int capacidade_da_turma(const char* turma_id){
    FILE *f = fopen("turmas.txt","r");
    if (!f) return -1;
    char line[512];
    int cap=-1;
    while (fgets(line,sizeof(line),f)){
        char id[100], nome[100], desc[200], prof[100];
        int c=0;
        if (sscanf(line,"%99[^;];%99[^;];%199[^;];%99[^;];%d", id,nome,desc,prof,&c)>=5){
            if (strcmp(id,turma_id)==0){ cap=c; break; }
        }
    }
    fclose(f);
    return cap;
}

static int alunos_matriculados_na_turma(const char* turma_id){
    ensure_file("matriculas.txt");
    FILE *f = fopen("matriculas.txt","r");
    if (!f) return 0;
    char line[256];
    int count=0;
    while (fgets(line,sizeof(line),f)){
        char t[100], aluno[100];
        if (sscanf(line,"%99[^;];%99[^\n]", t, aluno)==2){
            if (strcmp(t,turma_id)==0) count++;
        }
    }
    fclose(f);
    return count;
}

static int matricula_existe(const char* turma_id, const char* aluno_login){
    FILE *f = fopen("matriculas.txt","r");
    if (!f) return 0;
    char line[256];
    int found=0;
    while (fgets(line,sizeof(line),f)){
        char t[100], a[100];
        if (sscanf(line,"%99[^;];%99[^\n]", t,a)==2){
            if (strcmp(t,turma_id)==0 && strcmp(a,aluno_login)==0){ found=1; break; }
        }
    }
    fclose(f);
    return found;
}

static int turma_da_atividade(const char* atividade_id, char* turma_out, int turma_out_sz){
    FILE *f = fopen("atividades.txt","r");
    if (!f) return 0;
    char line[1024];
    int ok=0;
    while (fgets(line,sizeof(line),f)){
        char id[100], turma[100], titulo[200], desc[200], prazo[100], autor[100], entr[400];
        int n = sscanf(line,"%99[^;];%99[^;];%199[^;];%199[^;];%99[^;];%99[^;];%399[^\n]",
                       id,turma,titulo,desc,prazo,autor,entr);
        if (n>=2 && strcmp(id,atividade_id)==0){
            if (turma_out){
                strncpy(turma_out,turma,turma_out_sz-1);
                turma_out[turma_out_sz-1]='\0';
            }
            ok=1; break;
        }
    }
    fclose(f);
    return ok;
}

/* =========================
   Turmas
   ========================= */

EXPORT int criar_turma(const char* id, const char* nome, const char* descricao, const char* professor_login, int capacidade){
    if (!id || !nome || capacidade<1) return 2;

    if (!(eh_admin(professor_login) || eh_professor(professor_login))) return 2;

    FILE *f = fopen("turmas.txt","r");
    if (f){
        char line[512];
        while (fgets(line,sizeof(line),f)){
            char existing_id[100];
            if (sscanf(line,"%99[^;];", existing_id)==1){
                if (strcmp(existing_id,id)==0){ fclose(f); return 1; }
            }
        }
        fclose(f);
    }

    f = fopen("turmas.txt","a");
    if (!f) return 2;
    fprintf(f, "%s;%s;%s;%s;%d\n", id, nome, descricao?descricao:"", professor_login?professor_login:"", capacidade);
    fclose(f);
    return 0;
}

EXPORT int listar_turmas(char* buffer, int buffer_size){
    if (!buffer || buffer_size<=1) return 2;
    ensure_file("turmas.txt");
    FILE *f = fopen("turmas.txt","r");
    if (!f){
        strncpy(buffer, "Nenhuma turma cadastrada.\n", buffer_size-1);
        buffer[buffer_size-1]='\0';
        return 0;
    }
    buffer[0]='\0';
    char line[512];
    while (fgets(line,sizeof(line),f)){
        if ((int)(strlen(buffer)+strlen(line)+1)>=buffer_size){ fclose(f); return 1; }
        strcat(buffer,line);
    }
    fclose(f);
    return 0;
}

/* =========================
   Matrículas
   ========================= */

EXPORT int matricular_aluno(const char* turma_id, const char* aluno_login, const char* actor_login){
    if (!turma_id || !aluno_login || !actor_login) return 2;
    if (!buscar_tipo_usuario(aluno_login,NULL,0) || !eh_aluno(aluno_login)) return 4;

    /* permissão: admin ou professor dono da turma */
    if (!(eh_admin(actor_login) || professor_da_turma(actor_login, turma_id))) return 6;

    int cap = capacidade_da_turma(turma_id);
    if (cap<1) return 2; /* turma não encontrada */

    if (matricula_existe(turma_id, aluno_login)) return 3;

    int qty = alunos_matriculados_na_turma(turma_id);
    if (qty >= cap) return 1;

    FILE *f = fopen("matriculas.txt","a");
    if (!f) return 2;
    fprintf(f, "%s;%s\n", turma_id, aluno_login);
    fclose(f);
    return 0;
}

EXPORT int listar_alunos_da_turma(const char* turma_id, char* buffer, int buffer_size){
    if (!turma_id || !buffer || buffer_size<=1) return 2;
    ensure_file("matriculas.txt");
    FILE *f = fopen("matriculas.txt","r");
    if (!f){
        strncpy(buffer, "Nenhuma matrícula.\n", buffer_size-1);
        buffer[buffer_size-1]='\0';
        return 0;
    }
    buffer[0]='\0';
    char line[256];
    int any=0;
    while (fgets(line,sizeof(line),f)){
        char t[100], aluno[100];
        if (sscanf(line,"%99[^;];%99[^\n]", t, aluno)==2){
            if (strcmp(t,turma_id)==0){
                any=1;
                if ((int)(strlen(buffer)+strlen(aluno)+2)>=buffer_size){ fclose(f); return 1; }
                strcat(buffer, aluno); strcat(buffer, "\n");
            }
        }
    }
    fclose(f);
    if (!any){
        strncpy(buffer, "Nenhum aluno nesta turma.\n", buffer_size-1);
        buffer[buffer_size-1]='\0';
    }
    return 0;
}

EXPORT int listar_turmas_do_aluno(const char* aluno_login, char* buffer, int buffer_size){
    if (!aluno_login || !buffer || buffer_size<=1) return 2;
    ensure_file("matriculas.txt");
    FILE *f = fopen("matriculas.txt","r");
    if (!f){
        strncpy(buffer, "Sem matrículas.\n", buffer_size-1);
        buffer[buffer_size-1]='\0';
        return 0;
    }
    buffer[0]='\0';
    char line[256];
    int any=0;
    while (fgets(line,sizeof(line),f)){
        char t[100], a[100];
        if (sscanf(line,"%99[^;];%99[^\n]", t, a)==2){
            if (strcmp(a,aluno_login)==0){
                any=1;
                if ((int)(strlen(buffer)+strlen(t)+2)>=buffer_size){ fclose(f); return 1; }
                strcat(buffer, t); strcat(buffer,"\n");
            }
        }
    }
    fclose(f);
    if (!any){
        strncpy(buffer, "Você não está matriculado em nenhuma turma.\n", buffer_size-1);
        buffer[buffer_size-1]='\0';
    }
    return 0;
}

/* =========================
   Atividades
   ========================= */

EXPORT int criar_atividade(const char* id, const char* turma_id, const char* titulo, const char* descricao, const char* prazo, const char* autor_login) {
    if (!id || !turma_id || !titulo || !autor_login) return 2;

    if (!(eh_admin(autor_login) || professor_da_turma(autor_login, turma_id))) return 2;

    FILE *f = fopen("atividades.txt","a");
    if (!f) return 2;
    fprintf(f, "%s;%s;%s;%s;%s;%s;\n", id, turma_id, titulo, descricao?descricao:"", prazo?prazo:"", autor_login);
    fclose(f);
    return 0;
}

EXPORT int listar_atividades(char* buffer, int buffer_size){
    if (!buffer || buffer_size<=1) return 2;
    ensure_file("atividades.txt");
    FILE *f = fopen("atividades.txt","r");
    if (!f){
        strncpy(buffer, "Nenhuma atividade cadastrada.\n", buffer_size-1);
        buffer[buffer_size-1]='\0';
        return 0;
    }
    buffer[0]='\0';
    char line[1024];
    while (fgets(line,sizeof(line),f)){
        if ((int)(strlen(buffer)+strlen(line)+1)>=buffer_size){ fclose(f); return 1; }
        strcat(buffer,line);
    }
    fclose(f);
    return 0;
}

EXPORT int entregar_atividade(const char* atividade_id, const char* aluno_login){
    if (!atividade_id || !aluno_login) return 2;
    if (!eh_aluno(aluno_login)) return 2;

    char turma_id[100];
    if (!turma_da_atividade(atividade_id, turma_id, sizeof(turma_id))) return 1; /* atividade não existe */
    if (!matricula_existe(turma_id, aluno_login)) return 2; /* não pode entregar se não está na turma */

    FILE *f = fopen("atividades.txt","r");
    if (!f) return 2;
    char **lines=NULL; size_t count=0; char line[1024]; int found=0;
    while (fgets(line,sizeof(line),f)){
        char *copy=strdup(line);
        if (!copy){ fclose(f); return 2; }
        char id[100]={0}; sscanf(line,"%99[^;];", id);
        if (strcmp(id,atividade_id)==0) found=1;
        char **tmp=(char**)realloc(lines,sizeof(char*)*(count+1));
        if (!tmp){ fclose(f); free(copy); for(size_t j=0;j<count;j++) free(lines[j]); free(lines); return 2; }
        lines=tmp; lines[count++]=copy;
    }
    fclose(f);
    if (!found){ for(size_t i=0;i<count;i++) free(lines[i]); free(lines); return 1; }

    f = fopen("atividades.txt","w");
    if (!f){ for(size_t i=0;i<count;i++) free(lines[i]); free(lines); return 2; }

    for (size_t i=0;i<count;i++){
        char id[100]={0}, turma[100]={0}, titulo[200]={0}, desc[200]={0}, prazo[100]={0}, autor[100]={0}, entr[400]={0};
        char tmp[1024]; strncpy(tmp, lines[i], sizeof(tmp)-1); tmp[sizeof(tmp)-1]=0;
        int n = sscanf(tmp,"%99[^;];%99[^;];%199[^;];%199[^;];%99[^;];%99[^;];%399[^\n]", id,turma,titulo,desc,prazo,autor,entr);
        if (n>=2 && strcmp(id,atividade_id)==0){
            char novo[800]="";
            if (n>=7 && strlen(entr)>0) snprintf(novo,sizeof(novo), "%s,%s", entr, aluno_login);
            else snprintf(novo,sizeof(novo), "%s", aluno_login);
            fprintf(f,"%s;%s;%s;%s;%s;%s;%s\n", id,turma,titulo,desc,prazo,autor,novo);
        } else {
            fputs(lines[i], f);
        }
        free(lines[i]);
    }
    free(lines);
    fclose(f);
    return 0;
}

/* =========================
   Notas e Boletim
   ========================= */

static int nota_valida(const char* s){
    if (!s || !*s) return 0;
    char *end=NULL;
    double v = strtod(s,&end);
    if (end==s) return 0;
    if (v<0.0 || v>10.0) return 0;
    return 1;
}

EXPORT int lancar_nota(const char* turma_id, const char* aluno_login, const char* disciplina, const char* nota_str, const char* actor_login){
    if (!turma_id || !aluno_login || !disciplina || !nota_str || !actor_login) return 2;
    if (!eh_admin(actor_login) && !eh_professor(actor_login)) return 6;
    if (!eh_admin(actor_login) && !professor_da_turma(actor_login, turma_id)) return 6;

    if (!buscar_tipo_usuario(aluno_login,NULL,0) || !eh_aluno(aluno_login)) return 4;
    if (!nota_valida(nota_str)) return 2;
    if (!matricula_existe(turma_id, aluno_login)) return 5;

    FILE *f = fopen("notas.txt","a");
    if (!f) return 2;
    fprintf(f, "%s;%s;%s;%s\n", aluno_login, turma_id, disciplina, nota_str);
    fclose(f);
    return 0;
}

EXPORT int consultar_notas_aluno(const char* aluno_login, char* buffer, int buffer_size){
    if (!aluno_login || !buffer || buffer_size<=1) return 2;
    ensure_file("notas.txt");
    FILE *f = fopen("notas.txt","r");
    if (!f){
        strncpy(buffer, "Sem notas.\n", buffer_size-1);
        buffer[buffer_size-1]='\0';
        return 0;
    }
    buffer[0]='\0';
    char line[512];
    int any=0;
    while (fgets(line,sizeof(line),f)){
        char a[100], turma[100], disc[100], nota[50];
        if (sscanf(line, "%99[^;];%99[^;];%99[^;];%49[^\n]", a,turma,disc,nota)==4){
            if (strcmp(a,aluno_login)==0){
                any=1;
                char out[256];
                snprintf(out,sizeof(out), "Turma:%s | Disciplina:%s | Nota:%s\n", turma, disc, nota);
                if ((int)(strlen(buffer)+strlen(out)+1)>=buffer_size){ fclose(f); return 1; }
                strcat(buffer, out);
            }
        }
    }
    fclose(f);
    if (!any){
        strncpy(buffer, "Sem notas para este aluno.\n", buffer_size-1);
        buffer[buffer_size-1]='\0';
    }
    return 0;
}
static int qtd_meta_da_turma(const char* turma_id){
    if (!turma_id) return -1;
    ensure_file("turmas_meta.txt");
    FILE *f = fopen("turmas_meta.txt","r");
    if (!f) return -1;
    char line[256];
    int val = -1;
    while (fgets(line, sizeof(line), f)){
        char t[120]; int q=0;
        if (sscanf(line, "%119[^;];%d", t, &q)==2){
            if (strcmp(t, turma_id)==0){ val = q; break; }
        }
    }
    fclose(f);
    return val; 
}

static int bufcat(char* buffer, int buffer_size, const char* text){
    int cur = (int)strlen(buffer);
    int add = (int)strlen(text);
    if (cur + add >= buffer_size) return 1; 
    memcpy(buffer + cur, text, add + 1);
    return 0;
}

typedef struct {
    char turma[100];
    double soma;
    int count;
} AggTurma;

EXPORT int boletim_aluno(const char* aluno_login, char* buffer, int buffer_size){
    if (!aluno_login || !buffer || buffer_size<=1) return 2;

    ensure_file("notas.txt");
    FILE *f = fopen("notas.txt","r");
    if (!f){
        strncpy(buffer, "Sem notas.\n", buffer_size-1);
        buffer[buffer_size-1]='\0';
        return 0;
    }

    buffer[0] = '\0';

    AggTurma *aggs = NULL; int aggs_n = 0;

    char line[512];
    int any = 0;
    while (fgets(line,sizeof(line),f)){
        char a[120], turma[120], disc[200], nota_s[64];
        if (sscanf(line,"%119[^;];%119[^;];%199[^;];%63[^\n]", a,turma,disc,nota_s)==4){
            if (strcmp(a,aluno_login)!=0) continue;
            any = 1;

            /* aceitar vírgula como separador decimal */
            for (char *p=nota_s; *p; ++p) if (*p==',') *p='.';
            double v = atof(nota_s);

            char out[512];
            snprintf(out,sizeof(out), "Turma: %s | Disciplina: %s | Nota: %.2f\n", turma, disc, v);
            if (bufcat(buffer, buffer_size, out)){ fclose(f); free(aggs); return 1; }

            int idx = -1;
            for (int i=0;i<aggs_n;i++){
                if (strcmp(aggs[i].turma, turma)==0){ idx=i; break; }
            }
            if (idx<0){
                AggTurma *tmp = (AggTurma*)realloc(aggs, sizeof(AggTurma)*(aggs_n+1));
                if (!tmp){ fclose(f); free(aggs); return 2; }
                aggs = tmp; idx = aggs_n++;
                strncpy(aggs[idx].turma, turma, sizeof(aggs[idx].turma)-1);
                aggs[idx].turma[sizeof(aggs[idx].turma)-1] = '\0';
                aggs[idx].soma = 0.0;
                aggs[idx].count = 0;
            }
            aggs[idx].soma  += v;
            aggs[idx].count += 1;
        }
    }
    fclose(f);

    if (!any){
        strncpy(buffer, "Sem notas para este aluno.\n", buffer_size-1);
        buffer[buffer_size-1]='\0';
        free(aggs);
        return 0;
    }

    if (bufcat(buffer, buffer_size, "-----------------------------\n")){ free(aggs); return 1; }


    for (int i=0;i<aggs_n;i++){
        int qmeta = qtd_meta_da_turma(aggs[i].turma); 
        int denom = (qmeta>0 ? qmeta : aggs[i].count);
        if (denom <= 0) denom = aggs[i].count>0 ? aggs[i].count : 1;

        double media = aggs[i].soma / (double)denom;

        char out[256];
        snprintf(out, sizeof(out), "Média bimestre (%s): %.2f\n", aggs[i].turma, media);
        if (bufcat(buffer, buffer_size, out)){ free(aggs); return 1; }
    }

    free(aggs);
    return 0;
}
