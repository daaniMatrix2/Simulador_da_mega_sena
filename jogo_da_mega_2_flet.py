import flet as ft
import random
import io
import base64
import pandas as pd
# import openpyxl # Not used, can be removed if not needed elsewhere
import tempfile
import os

def main(page: ft.Page):
    page.title = "Jogo do Mega-Sena"
    # Centering might not be ideal with tabs, let Tabs handle expansion
    # page.vertical_alignment = ft.MainAxisAlignment.CENTER
    # page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.window_width = 750 # Adjusted width, tabs might need less horizontal space
    page.window_height = 800 # Adjusted height for better tab content visibility

    global listas_geradas, valor_do_jogo, historico_resultados # Add historico_resultados
    listas_geradas = []
    valor_do_jogo = 0
    historico_resultados = [] # Initialize historico_resultados list

    # --- Helper Functions ---
    def show_popup(title, message):
        """Helper to display simple popups."""
        dlg = ft.AlertDialog(
            title=ft.Text(title),
            content=ft.Text(message),
            actions=[ft.TextButton("OK", on_click=lambda e: close_dlg(e))],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.dialog = dlg
        dlg.open = True
        page.update()

    def close_dlg(e):
        """Close the currently open dialog."""
        if page.dialog:
            page.dialog.open = False
            page.update()

    # --- Core Logic Functions ---
    def gerar(e):
        global listas_geradas, valor_do_jogo
        listas_geradas = [] # Reset lists

        def gerar_listas_unicas(base_lista, num_listas, tamanho_lista):
            # Check if enough unique combinations are possible
            from math import comb
            if num_listas > comb(len(base_lista), tamanho_lista):
                 show_popup("Erro", f"Não é possível gerar {num_listas} combinações únicas de {tamanho_lista} números a partir de {len(base_lista)} números.")
                 return None # Indicate failure

            sequencias_unicas = set()
            while len(sequencias_unicas) < num_listas:
                # Ensure base_lista has enough elements for sampling
                if len(base_lista) < tamanho_lista:
                     show_popup("Erro", "A lista base tem menos números do que o tamanho desejado para cada jogo.")
                     return None # Indicate failure
                lista_embaralhada = random.sample(base_lista, tamanho_lista)
                sequencias_unicas.add(tuple(sorted(lista_embaralhada))) # Store sorted tuples for uniqueness
            return [list(seq) for seq in sequencias_unicas]

        try:
            # Validate and convert base list
            base_lista_str = tb1.value.strip()
            if not base_lista_str:
                show_popup("Erro", "A lista de números base não pode estar vazia.")
                return
            base_lista = list(map(int, base_lista_str.split(',')))
            if not all(1 <= num <= 60 for num in base_lista):
                 show_popup("Erro", "Os números na lista base devem estar entre 1 e 60.")
                 return
            if len(set(base_lista)) != len(base_lista):
                 show_popup("Erro", "A lista base contém números duplicados.")
                 return

            # Validate number of games
            num_listas_str = tb2.value.strip()
            if not num_listas_str.isdigit() or int(num_listas_str) <= 0:
                show_popup("Erro", "Por favor, insira um número válido e positivo de jogos.")
                return
            num_listas = int(num_listas_str)

            # Validate size of each game
            tamanho_lista_str = tb3.value.strip()
            if not tamanho_lista_str.isdigit() or not (6 <= int(tamanho_lista_str) <= 20):
                 show_popup("Erro", "O número de dezenas por jogo deve ser entre 6 e 20.")
                 return
            tamanho_lista = int(tamanho_lista_str)

            if tamanho_lista > len(base_lista):
                show_popup("Erro", f"O tamanho do jogo ({tamanho_lista}) não pode ser maior que a quantidade de números na lista base ({len(base_lista)}).")
                return

            # Calculate game cost
            custos = {
                6: 5.00, 7: 35.00, 8: 140.00, 9: 420.00, 10: 1050.00,
                11: 2310.00, 12: 4620.00, 13: 8580.00, 14: 15015.00, 15: 25025.00,
                16: 40040.00, 17: 61880.00, 18: 92820.00, 19: 135660.00, 20: 193800.00
            }
            valor_do_jogo = custos.get(tamanho_lista, 0) * num_listas
            valor_do_jogo_label.value = f"Valor Total: R$ {valor_do_jogo:.2f}"

            # Generate unique lists
            listas_geradas_temp = gerar_listas_unicas(base_lista, num_listas, tamanho_lista)
            if listas_geradas_temp is None: # Check if generation failed
                return # Error message was already shown

            listas_geradas = listas_geradas_temp # Assign if successful

            # Update ListView
            lv.controls.clear()
            for i, lista in enumerate(listas_geradas):
                # lista is already sorted from gerar_listas_unicas
                lista_sequencia = f"Jogo {i + 1}: {', '.join(map(str, lista))}"
                lv.controls.append(ft.Text(lista_sequencia))

            # Clear previous filter results if any
            label_sena.value = "Sena: 0"
            label_quina.value = "Quina: 0"
            label_quadra.value = "Quadra: 0"

            page.update()

        except ValueError:
            show_popup("Erro", "Por favor, verifique os valores inseridos. Use números inteiros separados por vírgula na lista base.")
        except Exception as ex:
             show_popup("Erro Inesperado", f"Ocorreu um erro: {ex}")


    def mostrar_listas_filtradas(e):
        global historico_resultados # Ensure we can modify the global list

        if not listas_geradas:
            show_popup("Aviso", "Gere os jogos primeiro antes de filtrar.")
            return

        try:
            numeros_escolhidos_string = tb4.value.strip()
            if not numeros_escolhidos_string:
                 show_popup("Erro", "Digite os 6 números sorteados.")
                 return

            numeros_escolhidos = list(map(int, numeros_escolhidos_string.split(',')))

            if len(numeros_escolhidos) != 6:
                show_popup("Erro", "Você deve digitar exatamente 6 números sorteados.")
                return
            if not all(1 <= num <= 60 for num in numeros_escolhidos):
                 show_popup("Erro", "Os números sorteados devem estar entre 1 e 60.")
                 return
            if len(set(numeros_escolhidos)) != 6:
                 show_popup("Erro", "Os números sorteados não podem ter repetições.")
                 return

            sena = 0
            quina = 0
            quadra = 0

            # Clear the ListView before adding filtered results
            lv.controls.clear()
            lv.controls.append(ft.Text(f"Conferindo contra: {', '.join(map(str, sorted(numeros_escolhidos)))}", weight="bold"))
            lv.controls.append(ft.Divider())

            jogos_premiados_encontrados = False
            for i, lista in enumerate(listas_geradas):
                # lista is already sorted
                correspondencias = set(lista) & set(numeros_escolhidos) # Use set intersection for efficiency
                num_correspondencias = len(correspondencias)

                if num_correspondencias >= 4:
                    jogos_premiados_encontrados = True
                    premio = ""
                    cor = "black" # Default color

                    if num_correspondencias == 6:
                        sena += 1
                        premio = "SENA"
                        cor = ft.colors.RED_ACCENT_700
                    elif num_correspondencias == 5:
                        quina += 1
                        premio = "QUINA"
                        cor = ft.colors.GREEN_ACCENT_700
                    elif num_correspondencias == 4:
                        quadra += 1
                        premio = "QUADRA"
                        cor = ft.colors.BLUE_ACCENT_700

                    resultado_text = f"Jogo {i + 1}: {', '.join(map(str, lista))} \n--> Acertos: {num_correspondencias} ({', '.join(map(str, sorted(list(correspondencias))))}) - {premio}"
                    lv.controls.append(ft.Text(resultado_text, color=cor, selectable=True))
                    lv.controls.append(ft.Divider(height=1, color=ft.colors.with_opacity(0.5, cor))) # Thin divider

            if not jogos_premiados_encontrados:
                 lv.controls.append(ft.Text("Nenhum jogo premiado (Quadra, Quina ou Sena) encontrado."))

            # Update result labels
            label_sena.value = f"Sena: {sena}"
            label_quina.value = f"Quina: {quina}"
            label_quadra.value = f"Quadra: {quadra}"

            # Add result summary to history list and ListView
            resultado_str = f"Sorteio ({', '.join(map(str, sorted(numeros_escolhidos)))}): Sena: {sena}, Quina: {quina}, Quadra: {quadra}"
            historical_lv.controls.append(ft.Text(resultado_str, size=14, selectable=True))
            historical_lv.controls.append(ft.Divider(height=1))
            historico_resultados.append(resultado_str) # Append string to the list for saving

            page.update()

        except ValueError:
            show_popup("Erro", "Por favor, insira 6 números válidos separados por vírgula.")
        except Exception as ex:
             show_popup("Erro Inesperado", f"Ocorreu um erro ao filtrar: {ex}")

    def limpar(e):
        global listas_geradas, valor_do_jogo, historico_resultados
        # Clear generated lists and history data
        listas_geradas = []
        historico_resultados = []

        # Clear ListViews
        lv.controls.clear()
        historical_lv.controls.clear()

        # Reset input fields
        # tb1.value = "" # Optional: clear inputs too?
        # tb2.value = ""
        # tb3.value = ""
        # tb4.value = ""

        # Reset result labels
        label_sena.value = "Sena: 0"
        label_quina.value = "Quina: 0"
        label_quadra.value = "Quadra: 0"
        valor_do_jogo_label.value = "Valor Total: R$ 0.00"
        valor_do_jogo = 0

        show_popup("Limpeza", "Dados gerados e históricos foram limpos.")
        page.update()

    def salvar_arquivo(e, tipo):
        """Salva as listas geradas ou o histórico em um arquivo .txt na área de trabalho."""
        data_to_save = []
        filename_base = ""
        no_data_message = ""

        if tipo == 'jogos':
            if not listas_geradas:
                show_popup("Aviso", "Não há jogos gerados para salvar.")
                return
            filename_base = "jogos_mega_sena_gerados"
            # Format data for saving (using the already sorted lists)
            for i, lista in enumerate(listas_geradas):
                 data_to_save.append(f"Jogo {i + 1}: {', '.join(map(str, lista))}")
        elif tipo == 'historico':
            if not historico_resultados:
                show_popup("Aviso", "Não há histórico de conferências para salvar.")
                return
            filename_base = "historico_conferencias_mega_sena"
            data_to_save = historico_resultados # Already formatted strings
        else:
            return # Should not happen

        # Nome do arquivo
        nome_arquivo = f"{filename_base}.txt"

        # Caminho para a área de trabalho do usuário
        try:
            caminho_area_de_trabalho = os.path.join(os.path.expanduser("~"), "Desktop")
            if not os.path.exists(caminho_area_de_trabalho):
                 # Fallback to user's home directory if Desktop doesn't exist
                 caminho_area_de_trabalho = os.path.expanduser("~")

            caminho_arquivo = os.path.join(caminho_area_de_trabalho, nome_arquivo)

            # Criando e escrevendo o conteúdo no arquivo
            with open(caminho_arquivo, 'w', encoding='utf-8') as f:
                for linha in data_to_save:
                    f.write(f"{linha}\n")

            show_popup("Sucesso", f"Arquivo '{nome_arquivo}' foi salvo em:\n{caminho_area_de_trabalho}")

        except Exception as ex:
            show_popup("Erro ao Salvar", f"Ocorreu um erro ao salvar o arquivo: {ex}")

    # --- UI Controls Definition ---

    # Labels for results
    label_sena = ft.Text("Sena: 0", size=20, color=ft.colors.RED_ACCENT_700, weight="bold")
    label_quina = ft.Text("Quina: 0", size=20, color=ft.colors.GREEN_ACCENT_700, weight="bold")
    label_quadra = ft.Text("Quadra: 0", size=20, color=ft.colors.BLUE_ACCENT_700, weight="bold")
    valor_do_jogo_label = ft.Text("Valor Total: R$ 0.00", size=16, color="black", italic=True)

    # Input TextFields
    tb1 = ft.TextField(
        label="Números Base (ex: 1,5,10,22,30,45,55,60)",
        hint_text="Digite de 6 a 60 números, separados por vírgula",
        expand=True, # Allow it to take available width in the row
    )
    tb2 = ft.TextField(
        label="Quantos jogos?",
        hint_text="Ex: 10",
        width=150, # Fixed width
        input_filter=ft.InputFilter(allow=True, regex_string=r"[0-9]", replacement_string=""),
    )
    tb3 = ft.TextField(
        label="Dezenas por jogo?",
        hint_text="6 a 20",
        width=150, # Fixed width
        input_filter=ft.InputFilter(allow=True, regex_string=r"[0-9]", replacement_string=""),
    )
    tb4 = ft.TextField(
        label="Conferir resultado (6 números sorteados)",
        hint_text="Ex: 4,17,23,30,45,59",
        expand=True, # Allow it to take available width in the row
    )

    # Buttons
    button_gerar_jogo = ft.FilledButton(
        text="Gerar Jogos",
        icon=ft.icons.CASINO,
        on_click=gerar
    )
    button_valida_bilhete = ft.FilledButton(
        text="Conferir Jogos",
        icon=ft.icons.CHECK_CIRCLE_OUTLINE,
        on_click=mostrar_listas_filtradas
    )
    button_limpar_historico = ft.ElevatedButton(
        text="Limpar Tudo",
        icon=ft.icons.CLEAR_ALL,
        color=ft.colors.WHITE,
        bgcolor=ft.colors.RED_400,
        on_click=limpar
    )
    button_download_jogos = ft.OutlinedButton(
        text="Salvar Jogos",
        icon=ft.icons.SAVE_ALT,
        tooltip="Salvar jogos gerados na Área de Trabalho",
        on_click=lambda e: salvar_arquivo(e, 'jogos') # Pass type
    )
    button_download_historico = ft.OutlinedButton(
        text="Salvar Histórico",
        icon=ft.icons.SAVE_ALT,
        tooltip="Salvar histórico de conferências na Área de Trabalho",
        on_click=lambda e: salvar_arquivo(e, 'historico') # Pass type
    )

    # ListViews and Containers
    lv = ft.ListView(expand=True, spacing=5, padding=10, auto_scroll=True) # expand=True to fill container
    lv_container = ft.Container(
        content=lv,
        # margin=10, # Margin handled by parent container/padding
        padding=5,
        border=ft.border.all(1, color=ft.colors.BLUE_GREY_300),
        border_radius=8,
        expand=True # Make container fill available space in its parent Column
        # Removed fixed height/width to allow expansion
    )

    historical_lv = ft.ListView(expand=True, spacing=5, padding=10, auto_scroll=True) # expand=True
    historical_lv_container = ft.Container(
        content=historical_lv,
        # margin=10,
        padding=5,
        border=ft.border.all(1, color=ft.colors.GREEN_700),
        border_radius=8,
        expand=True # Make container fill available space in its parent Column
        # Removed fixed height/width to allow expansion
    )

    # --- Define Content for Each Tab ---

    # Tab 1: Controls and Configuration
    tab_content_controles = ft.Container(
        padding=20,
        alignment=ft.alignment.top_center,
        content=ft.Column(
            controls=[
                ft.Text("Configuração dos Jogos", size=18, weight="bold"),
                ft.Row(controls=[tb1]),
                ft.Row(controls=[tb2, tb3], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Row(controls=[button_gerar_jogo], alignment=ft.MainAxisAlignment.CENTER),
                ft.Divider(height=10, color=ft.colors.TRANSPARENT), # Spacer

                ft.Text("Conferência de Resultados", size=18, weight="bold"),
                ft.Row(controls=[tb4]),
                ft.Row(controls=[button_valida_bilhete], alignment=ft.MainAxisAlignment.CENTER),
                ft.Divider(height=10, color=ft.colors.TRANSPARENT), # Spacer

                ft.Text("Resumo da Conferência", size=18, weight="bold"),
                ft.Row(
                    controls=[label_quadra, label_quina, label_sena],
                    alignment=ft.MainAxisAlignment.SPACE_AROUND # Distribute labels
                ),
                 ft.Row(
                    controls=[valor_do_jogo_label],
                    alignment=ft.MainAxisAlignment.CENTER
                ),
                ft.Divider(height=10, color=ft.colors.TRANSPARENT), # Spacer
                ft.Row(controls=[button_limpar_historico], alignment=ft.MainAxisAlignment.CENTER),
            ],
            spacing=15, # Vertical spacing between elements in the column
            scroll=ft.ScrollMode.ADAPTIVE # Allow scrolling if content overflows
        )
    )

    # Tab 2: Generated/Filtered Lists
    tab_content_jogos = ft.Container(
        padding=15,
        expand=True, # Allow this container to expand vertically
        content=ft.Column(
             controls=[
                ft.Row(
                    controls=[
                        ft.Text("Jogos Gerados / Conferidos", size=18, weight="bold", expand=True, text_align=ft.TextAlign.CENTER),
                        button_download_jogos # Place button next to title
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                lv_container, # This container will expand due to expand=True
            ],
            expand=True # Allow Column to expand vertically
        )
    )

    # Tab 3: History
    tab_content_historico = ft.Container(
        padding=15,
        expand=True, # Allow this container to expand vertically
        content=ft.Column(
            controls=[
                 ft.Row(
                    controls=[
                        ft.Text("Histórico de Conferências", size=18, weight="bold", expand=True, text_align=ft.TextAlign.CENTER),
                        button_download_historico # Place button next to title
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                historical_lv_container, # This container will expand due to expand=True
            ],
            expand=True # Allow Column to expand vertically
        )
    )

    # --- Create Tabs ---
    tabs_main = ft.Tabs(
        selected_index=0,
        animation_duration=300,
        tabs=[
            ft.Tab(
                text="Configurar & Conferir",
                icon=ft.icons.SETTINGS_APPLICATIONS_SHARP,
                content=tab_content_controles,
            ),
            ft.Tab(
                text="Jogos",
                icon=ft.icons.LIST_ALT_SHARP,
                content=tab_content_jogos,
            ),
            ft.Tab(
                text="Histórico",
                icon=ft.icons.HISTORY_EDU_SHARP,
                content=tab_content_historico,
            ),
        ],
        expand=1 # Make the Tabs control fill the page
    )

    # --- Add Tabs to Page ---
    page.add(tabs_main)
    page.update() # Ensure initial layout is rendered

# --- Run the App ---
if __name__ == "__main__":
    ft.app(target=main)
