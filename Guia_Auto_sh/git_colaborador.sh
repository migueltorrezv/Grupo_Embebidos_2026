#!/bin/bash

# =============================================================================
#  GIT COLABORADOR — Embedded Systems II
#  Repo: migueltorrezv / Grupo_Embebidos_2026
#  Para: compañeros del grupo
# =============================================================================

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

CONFIG_FILE="$HOME/.git_colab_config"

# ── Datos fijos del repo ──────────────────────────────────────────────────────
REPO_URL="https://github.com/migueltorrezv/Grupo_Embebidos_2026.git"
REPO_DIR="$HOME/Grupo_Embebidos_2026"

# =============================================================================
#  UTILIDADES
# =============================================================================

print_banner() {
    clear
    echo -e "${CYAN}"
    echo "  ╔══════════════════════════════════════════════════════╗"
    echo "  ║     GIT COLABORADOR — Embedded Systems II           ║"
    echo "  ║     Repo: Grupo_Embebidos_2026                      ║"
    echo "  ╚══════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_success() { echo -e "${GREEN}  ✔  $1${NC}"; }
print_error()   { echo -e "${RED}  ✘  $1${NC}"; }
print_info()    { echo -e "${BLUE}  ℹ  $1${NC}"; }
print_warn()    { echo -e "${YELLOW}  ⚠  $1${NC}"; }
print_step()    { echo -e "${BOLD}  ──▶  $1${NC}"; }
separator()     { echo -e "${CYAN}  ────────────────────────────────────────────────────${NC}"; }

check_git() {
    if ! command -v git &> /dev/null; then
        print_error "Git no está instalado."
        print_info  "Instálalo con: sudo apt install git"
        exit 1
    fi
}

save_config() {
    cat > "$CONFIG_FILE" <<EOF
MY_NAME="$MY_NAME"
MY_EMAIL="$MY_EMAIL"
EOF
    chmod 600 "$CONFIG_FILE"
}

load_config() {
    [ -f "$CONFIG_FILE" ] && source "$CONFIG_FILE" && return 0
    return 1
}

check_repo() {
    if [ ! -d "$REPO_DIR/.git" ]; then
        print_error "Repositorio no encontrado."
        print_info  "Usa la opción 1 primero."
        return 1
    fi
    return 0
}

show_status() {
    separator
    print_info "Estado actual:"
    cd "$REPO_DIR" || return
    git status --short
    echo ""
    print_info "Rama: $(git branch --show-current)"
    print_info "Último commit: $(git log --oneline -1 2>/dev/null || echo 'Sin commits')"
    separator
}

# =============================================================================
#  OPCIÓN 1 — CONFIGURAR Y CLONAR  (solo la primera vez)
# =============================================================================

setup_and_clone() {
    print_banner
    echo -e "${BOLD}  ═══ CONFIGURACIÓN INICIAL ═══${NC}"
    separator
    echo ""
    echo -e "  ${YELLOW}Solo necesitas hacer esto UNA VEZ.${NC}"
    echo ""

    # ── Datos personales ──────────────────────────────────────────────────────
    read -p "  Tu nombre (aparece en los commits): " MY_NAME
    read -p "  Tu email de GitHub:                 " MY_EMAIL

    git config --global user.name  "$MY_NAME"
    git config --global user.email "$MY_EMAIL"
    git config --global pull.rebase false

    # ── Token personal ────────────────────────────────────────────────────────
    echo ""
    separator
    echo -e "  ${BOLD}Configuración de tu token de GitHub${NC}"
    separator
    echo ""
    echo -e "  Necesitas un token para poder subir cambios."
    echo -e "  Sigue estos pasos en GitHub con ${BOLD}tu propia cuenta${NC}:"
    echo ""
    echo -e "  ${CYAN}1.${NC} Ve a: github.com → inicia sesión con tu cuenta"
    echo -e "  ${CYAN}2.${NC} Click en tu foto (arriba a la derecha) → ${BOLD}Settings${NC}"
    echo -e "  ${CYAN}3.${NC} Baja hasta el final → ${BOLD}Developer settings${NC}"
    echo -e "  ${CYAN}4.${NC} ${BOLD}Personal access tokens${NC} → ${BOLD}Tokens (classic)${NC}"
    echo -e "  ${CYAN}5.${NC} ${BOLD}Generate new token${NC} → ${BOLD}Generate new token (classic)${NC}"
    echo -e "  ${CYAN}6.${NC} En Note escribe: ${CYAN}Embedded Systems 2026${NC}"
    echo -e "  ${CYAN}7.${NC} En Expiration elige: ${CYAN}No expiration${NC}"
    echo -e "  ${CYAN}8.${NC} Marca el permiso: ${CYAN}✅ repo${NC} (el primero)"
    echo -e "  ${CYAN}9.${NC} Click en ${BOLD}Generate token${NC} (botón verde)"
    echo -e "  ${CYAN}10.${NC} ${RED}COPIA el token — solo se muestra una vez${NC}"
    echo ""
    echo -e "  El token se ve así: ${CYAN}ghp_xxxxxxxxxxxxxxxxxxxx${NC}"
    echo ""
    read -p "  ¿Ya tienes tu token listo? (s/N): " ready
    ready="${ready:-n}"

    if [[ "$ready" =~ ^[sS]$ ]]; then
        read -s -p "  Pega tu token aquí (no se verá): " MY_TOKEN
        echo ""
        if [ -n "$MY_TOKEN" ]; then
            # Guardar token en config
            cat > "$CONFIG_FILE" <<EOF
MY_NAME="$MY_NAME"
MY_EMAIL="$MY_EMAIL"
MY_TOKEN="$MY_TOKEN"
EOF
            chmod 600 "$CONFIG_FILE"
            # Guardar credenciales en git para no pedirlas cada vez
            git config --global credential.helper store
            print_success "Token guardado correctamente"
        else
            print_warn "Token vacío. Puedes ejecutar la opción 1 de nuevo para agregarlo."
            cat > "$CONFIG_FILE" <<EOF
MY_NAME="$MY_NAME"
MY_EMAIL="$MY_EMAIL"
MY_TOKEN=""
EOF
            chmod 600 "$CONFIG_FILE"
        fi
    else
        print_warn "Sin token por ahora. Recuerda que lo necesitas para subir cambios."
        cat > "$CONFIG_FILE" <<EOF
MY_NAME="$MY_NAME"
MY_EMAIL="$MY_EMAIL"
MY_TOKEN=""
EOF
        chmod 600 "$CONFIG_FILE"
    fi

    print_success "Configuración guardada: $MY_NAME"

    # ── Clonar ────────────────────────────────────────────────────────────────
    echo ""
    separator
    if [ -d "$REPO_DIR/.git" ]; then
        print_warn "El repositorio ya está clonado en: $REPO_DIR"
        return
    fi

    mkdir -p "$(dirname "$REPO_DIR")"
    print_step "Clonando repositorio del grupo..."

    # Usar token en la URL si está disponible
    local clone_url="$REPO_URL"
    if [ -n "$MY_TOKEN" ]; then
        clone_url="https://${MY_TOKEN}@github.com/migueltorrezv/Grupo_Embebidos_2026.git"
    fi

    if git clone "$clone_url" "$REPO_DIR"; then
        cd "$REPO_DIR" && git remote set-url origin "$REPO_URL"
        print_success "¡Repositorio clonado en: $REPO_DIR!"
        echo ""
        print_info "La próxima vez puedes ir directo a la opción 2 o 3."
    else
        echo ""
        print_error "Error al clonar."
        echo ""
        echo -e "  Verifica que:"
        echo -e "  · Tienes conexión a internet"
        echo -e "  · ${YELLOW}migueltorrezv te agregó como colaborador en GitHub${NC}"
        echo -e "  · Aceptaste la invitación que llegó a tu email"
        echo -e "  · Tu token es correcto"
    fi
}

# =============================================================================
#  OPCIÓN 2 — SUBIR MIS CAMBIOS
# =============================================================================

push_changes() {
    print_banner
    echo -e "${BOLD}  ═══ SUBIR MIS CAMBIOS ═══${NC}"
    separator
    load_config
    check_repo || return
    cd "$REPO_DIR" || return

    # Verificar si hay cambios nuevos del grupo antes de subir
    print_step "Verificando cambios del grupo..."
    git fetch origin &>/dev/null

    current_branch=$(git branch --show-current)
    behind=$(git rev-list HEAD..origin/"$current_branch" --count 2>/dev/null || echo 0)

    if [ "$behind" -gt 0 ]; then
        print_warn "Hay $behind commit(s) nuevos del grupo que no tienes."
        read -p "  ¿Bajarlos primero? (recomendado) (S/n): " do_pull
        do_pull="${do_pull:-s}"
        if [[ "$do_pull" =~ ^[sS]$ ]]; then
            git pull origin "$current_branch" \
                && print_success "Cambios del grupo descargados" \
                || { print_error "Error al bajar cambios."; return; }
        fi
    fi

    # Verificar si hay algo para subir
    if git diff --quiet && git diff --staged --quiet \
       && [ -z "$(git ls-files --others --exclude-standard)" ]; then
        print_warn "No tienes cambios locales para subir."
        show_status
        return
    fi

    show_status

    echo -e "  ¿Qué deseas subir?"
    echo -e "  ${CYAN}1)${NC} Todo lo que modifiqué"
    echo -e "  ${CYAN}2)${NC} Solo mi carpeta de lab"
    echo -e "  ${CYAN}3)${NC} Archivos específicos"
    read -p "  Opción [1]: " add_opt
    add_opt="${add_opt:-1}"

    case $add_opt in
        1)
            git add .
            print_success "Todo en staging"
            ;;
        2)
            echo ""
            ls -d */ 2>/dev/null | nl -w2 -s") "
            read -p "  Nombre de tu carpeta (ej: lab_1): " folder
            if [ -d "$folder" ]; then
                git add "$folder"
                print_success "Carpeta '$folder' añadida"
            else
                print_error "Carpeta no encontrada."
                return
            fi
            ;;
        3)
            git status --short
            read -p "  Archivos (separados por espacio): " files
            # shellcheck disable=SC2086
            git add $files
            ;;
        *) print_error "Inválido"; return ;;
    esac

    echo ""
    echo -e "  Describe brevemente qué hiciste:"
    echo -e "  ${CYAN}Ej: lab_2 terminado — control de motor${NC}"
    read -p "  ▶ " commit_msg

    if [ -z "$commit_msg" ]; then
        commit_msg="Cambios de $MY_NAME — $(date '+%Y-%m-%d %H:%M')"
        print_warn "Usando: '$commit_msg'"
    fi

    git commit -m "$commit_msg" || { print_error "Error en commit."; return; }
    print_success "Commit: '$commit_msg'"

    print_step "Subiendo a GitHub..."

    local push_url="$REPO_URL"
    if [ -n "$MY_TOKEN" ]; then
        push_url="https://${MY_TOKEN}@github.com/migueltorrezv/Grupo_Embebidos_2026.git"
    fi

    git remote set-url origin "$push_url"
    if git push origin "$current_branch"; then
        git remote set-url origin "$REPO_URL"
        print_success "¡Cambios subidos correctamente!"
        print_info "Commit: $(git log --oneline -1)"
    else
        git remote set-url origin "$REPO_URL"
        echo ""
        print_error "Error al subir."
        echo ""
        echo -e "  Verifica que:"
        echo -e "  · ${YELLOW}migueltorrezv te agregó como colaborador${NC}"
        echo -e "  · Aceptaste la invitación de GitHub"
        echo -e "  · Tu token es válido (opción 1 para actualizarlo)"
        echo -e "  · Tienes conexión a internet"
    fi
}

# =============================================================================
#  OPCIÓN 3 — BAJAR CAMBIOS DEL GRUPO
# =============================================================================

pull_changes() {
    print_banner
    echo -e "${BOLD}  ═══ BAJAR CAMBIOS DEL GRUPO ═══${NC}"
    separator
    check_repo || return
    cd "$REPO_DIR" || return

    current_branch=$(git branch --show-current)
    print_step "Descargando últimos cambios..."

    if git pull origin "$current_branch"; then
        print_success "¡Repositorio actualizado!"
    else
        print_error "Error al bajar cambios."
        print_info  "Avisa a migueltorrezv si el problema persiste."
    fi

    show_status
}

# =============================================================================
#  OPCIÓN 4 — CREAR CARPETA DE LAB
# =============================================================================

create_lab() {
    print_banner
    echo -e "${BOLD}  ═══ NUEVA CARPETA ═══${NC}"
    separator
    check_repo || return
    cd "$REPO_DIR" || return

    echo ""
    echo -e "  Puedes escribir:"
    echo -e "  · Un ${CYAN}número${NC}: 1=lab  2=proyecto  3=tarea  4=personalizado"
    echo -e "  · O directamente el ${CYAN}nombre${NC}: lab_4, proyecto_2, mi_carpeta..."
    echo ""
    read -p "  Tipo o nombre [1]: " tipo
    tipo="${tipo:-1}"

    # Si escribió directamente un nombre con formato (ej: lab_4, proyecto_2)
    if [[ "$tipo" =~ ^(lab|proyecto|tarea)_[0-9]+$ ]]; then
        folder_name="$tipo"
        prefix=""
    # Si escribió cualquier otro nombre que no sea 1/2/3/4
    elif [[ ! "$tipo" =~ ^[1-4]$ ]]; then
        folder_name="$tipo"
        prefix=""
    else
        case $tipo in
            1) prefix="lab" ;;
            2) prefix="proyecto" ;;
            3) prefix="tarea" ;;
            4) read -p "  Nombre de la carpeta: " folder_name; prefix="" ;;
        esac

        if [ -n "$prefix" ]; then
            last=$(ls -d ${prefix}_* 2>/dev/null | grep -oP '\d+' | sort -n | tail -1)
            next=$((${last:-0} + 1))
            read -p "  Número [$next]: " num
            num="${num:-$next}"
            folder_name="${prefix}_${num}"
        fi
    fi

    mkdir -p "$folder_name"
    cd "$folder_name" || return

    echo ""
    echo -e "  Archivos base:"
    echo -e "  ${CYAN}1)${NC} README + main.py"
    echo -e "  ${CYAN}2)${NC} README + main.c + Makefile"
    echo -e "  ${CYAN}3)${NC} Solo README"
    echo -e "  ${CYAN}4)${NC} Ninguno"
    read -p "  Opción [1]: " fopt
    fopt="${fopt:-1}"

    gen_readme() {
        cat > README.md <<EOF
# ${folder_name^^}
**Materia:** Embedded Systems II | **Fecha:** $(date +%d/%m/%Y)

## Objetivo
<!-- Describe el objetivo -->

## Desarrollo
<!-- Explica lo que hiciste -->

## Resultados
<!-- Capturas o explicaciones -->
EOF
        print_success "README.md creado"
    }

    case $fopt in
        1)
            gen_readme
            cat > main.py <<EOF
# $folder_name — Embedded Systems II
# Fecha: $(date +%d/%m/%Y)

def main():
    pass

if __name__ == "__main__":
    main()
EOF
            print_success "main.py creado"
            ;;
        2)
            gen_readme
            cat > main.c <<EOF
/* $folder_name — Embedded Systems II — $(date +%d/%m/%Y) */
#include <stdio.h>

int main(void) {
    return 0;
}
EOF
            cat > Makefile <<EOF
CC=gcc
CFLAGS=-Wall -Wextra -std=c11
TARGET=main

all: \$(TARGET)
\$(TARGET): main.c
	\$(CC) \$(CFLAGS) -o \$@ $<
clean:
	rm -f \$(TARGET)
.PHONY: all clean
EOF
            print_success "main.c + Makefile creados"
            ;;
        3) gen_readme ;;
        4) ;;
    esac

    cd "$REPO_DIR"
    print_success "¡Carpeta '$folder_name' lista!"
    show_status
}

# =============================================================================
#  OPCIÓN 5 — HISTORIAL
# =============================================================================

show_history() {
    print_banner
    echo -e "${BOLD}  ═══ HISTORIAL DEL GRUPO ═══${NC}"
    separator
    check_repo || return
    cd "$REPO_DIR" || return
    echo ""
    git log --oneline --graph --decorate --color -15
    echo ""
    separator
}

# =============================================================================
#  MENÚ PRINCIPAL
# =============================================================================

main_menu() {
    while true; do
        print_banner
        load_config

        if [ -d "$REPO_DIR/.git" ]; then
            cd "$REPO_DIR" 2>/dev/null
            echo -e "  ${CYAN}Hola, ${MY_NAME:-Colaborador}!${NC}"
            echo -e "  ${CYAN}Repo:${NC} Grupo_Embebidos_2026"
            echo -e "  ${CYAN}Rama:${NC} $(git branch --show-current 2>/dev/null)"
        else
            echo -e "  ${YELLOW}⚠  Primera vez — usa la opción 1${NC}"
        fi

        separator
        echo ""
        echo -e "  ${BOLD}¿Qué deseas hacer?${NC}"
        echo ""
        echo -e "  ${CYAN} 1)${NC} ⚙️  Configurar y clonar   ${YELLOW}(solo la primera vez)${NC}"
        echo -e "  ${CYAN} 2)${NC} 🚀 Subir mis cambios"
        echo -e "  ${CYAN} 3)${NC} 📡 Bajar cambios del grupo"
        echo -e "  ${CYAN} 4)${NC} 📁 Crear carpeta de lab/proyecto"
        echo -e "  ${CYAN} 5)${NC} 📜 Ver historial del grupo"
        echo -e "  ${CYAN} 0)${NC} 🚪 Salir"
        echo ""
        separator
        read -p "  Opción: " option

        case $option in
            1) setup_and_clone ;;
            2) push_changes    ;;
            3) pull_changes    ;;
            4) create_lab      ;;
            5) show_history    ;;
            0) echo ""; print_success "¡Hasta luego! 💪"; echo ""; exit 0 ;;
            *) print_error "Opción inválida" ;;
        esac

        echo ""
        read -p "  Presiona ENTER para continuar..."
    done
}

# =============================================================================
check_git
main_menu
