import flet as ft
import random
import io
import base64
import pandas as pd
import openpyxl
import tempfile
import os

def main(page: ft.Page):
    page.title = "Jogo do Mega-Sena"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.window_width = 1700
    page.window_height = 650

    global listas_geradas  # Definindo global para acessibilidade
    listas_geradas = []  # Inicializa as listas geradas
    global valor_do_jogo
    valor_do_jogo = 0  # Inicializa a variável

    def gerar(e):
        global listas_geradas
        listas_geradas = []
        global valor_do_jogo

        def gerar_listas_unicas(base_lista, num_listas, tamanho_lista):
            sequencias_unicas = set()
            while len(sequencias_unicas) < num_listas:
                lista_embaralhada = random.sample(base_lista, tamanho_lista)
                sequencias_unicas.add(tuple(lista_embaralhada))
            return [list(seq) for seq in sequencias_unicas]

        try:
            # Converte o valor do campo tb1 em uma lista de inteiros
            base_lista = list(map(int, tb1.value.split(',')))
            num_listas = int(tb2.value)  # Número de jogos
            tamanho_lista = int(tb3.value)  # Tamanho de cada lista

            # Definindo o valor do jogo com base no tamanho da lista
            if tamanho_lista == 6:
                valor_do_jogo = 5.00 * num_listas
            elif tamanho_lista == 7:
                valor_do_jogo = 35.00 * num_listas
            elif tamanho_lista == 8:
                valor_do_jogo = 140.00 * num_listas
            elif tamanho_lista == 9:
                valor_do_jogo = 420.00 * num_listas
            elif tamanho_lista == 10:
                valor_do_jogo = 1050.00 * num_listas
            elif tamanho_lista == 11:
                valor_do_jogo = 2310.00 * num_listas
            elif tamanho_lista == 12:
                valor_do_jogo = 4620.00 * num_listas
            elif tamanho_lista == 13:
                valor_do_jogo = 8580.00 * num_listas
            elif tamanho_lista == 14:
                valor_do_jogo = 15015.00 * num_listas
            elif tamanho_lista == 15:
                valor_do_jogo = 25025.00 * num_listas
            elif tamanho_lista == 16:
                valor_do_jogo = 40040.00 * num_listas
            elif tamanho_lista == 17:
                valor_do_jogo = 61880.00 * num_listas
            elif tamanho_lista == 18:
                valor_do_jogo = 92820.00 * num_listas
            elif tamanho_lista == 19:
                valor_do_jogo = 135660.00 * num_listas
            elif tamanho_lista == 20:
                valor_do_jogo = 193800.00 * num_listas

            # Atualiza o label do valor do jogo
            valor_do_jogo_label.value = f"Valor do jogo: R$ {valor_do_jogo:.2f}"

            if tamanho_lista > len(base_lista):
                ft.popup("Erro", "O tamanho da lista não pode ser maior que o número de elementos na base lista.")
                return

            listas_geradas = gerar_listas_unicas(base_lista, num_listas, tamanho_lista)

            # Limpar a ListView antes de adicionar novas entradas
            lv.controls.clear()

            for i, lista in enumerate(listas_geradas):
                lista_ordenada = sorted(lista)
                lista_sequencia = f"Lista {i + 1}: {lista_ordenada}"
                lv.controls.append(ft.Text(lista_sequencia))  # Adicionar a nova lista à ListView

            page.update()  # Atualiza a página para refletir as mudanças na ListView

        except ValueError:
            ft.popup("Erro", "Por favor, insira valores válidos.")


    def gerar_arquivo_download(e):
        if not listas_geradas:
            ft.popup("Erro", "Não há listas geradas para baixar.")
            return

        # Usar tempfile para criar um arquivo temporário
        with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as temp_file:
            # Escrever as listas geradas no arquivo
            for i, lista in enumerate(listas_geradas):
                temp_file.write(f"Lista {i + 1}: {', '.join(map(str, sorted(lista))) }\n".encode('utf-8'))
            temp_file_path = temp_file.name  # Guarda o caminho do arquivo temporário
        
        # Forçar o download do arquivo com o caminho apropriado
        page.launch_url(f"file://{temp_file_path}")
        
        # Criar conteúdo do arquivo
        output = io.StringIO()
        for i, lista in enumerate(listas_geradas):
            output.write(f"Lista {i + 1}: {', '.join(map(str, sorted(lista))) }\n")
        
        # Codificar o conteúdo
        file_content = output.getvalue()
        output.close()
        
        # Codificar em base64 para download
        encoded = base64.b64encode(file_content.encode('utf-8')).decode('utf-8')

        # Criar link para download do arquivo de texto
        link = f"data:text/plain;base64,{encoded}"
        page.launch_url(link)

    def salvar_arquivo(e):
        # Verificando se há listas geradas
        if not listas_geradas:
            ft.popup("Erro", "Não há listas geradas para salvar.")
            return

        # Nome do arquivo
        nome_arquivo = "lista_dos_numeros_da_mega_sena.txt"

        # Caminho para a área de trabalho do usuário
        caminho_area_de_trabalho = os.path.join(os.path.expanduser("~"), "Desktop")
        caminho_arquivo = os.path.join(caminho_area_de_trabalho, nome_arquivo)

        try:
            # Criando e escrevendo o conteúdo no arquivo
            with open(caminho_arquivo, 'w') as f:
                for i, lista in enumerate(listas_geradas):
                    f.write(f"Lista {i + 1}: {', '.join(map(str, sorted(lista))) }\n")

            ft.popup("Sucesso", f"{nome_arquivo} foi salvo na área de trabalho!")

        except Exception as e:
            ft.popup("Erro", f"Ocorreu um erro ao salvar o arquivo: {e}")

    def salvar_arquivo_historico(e):
        global historico_resultados  # Deixe: lista acessível

        # Verificando se há listas geradas
        if not historico_resultados:
            ft.popup("Erro", "Não há listas geradas para salvar.")
            return

        # Nome do arquivo
        nome_arquivo = "historico_da_mega.txt"

        # Caminho para a área de trabalho do usuário
        caminho_area_de_trabalho = os.path.join(os.path.expanduser("~"), "Desktop")
        caminho_arquivo = os.path.join(caminho_area_de_trabalho, nome_arquivo)

        try:
            # Criando e escrevendo o conteúdo no arquivo
            with open(caminho_arquivo, 'w') as f:
                for resultado in historico_resultados:
                    f.write(f"{resultado}\n")  # Escrevendo cada resultado da lista

            ft.popup("Sucesso", f"{nome_arquivo} foi salvo na área de trabalho!")

        except Exception as e:
            ft.popup("Erro", f"Ocorreu um erro ao salvar o arquivo: {e}")


    def limpar(e):
        # Limpa a ListView de resultados e o histórico
        lv.controls.clear()
        historical_lv.controls.clear()
        
        # Atualiza labels de resultados
        label_sena.value = "Sena: 0"
        label_quina.value = "Quina: 0"
        label_quadra.value = "Quadra: 0"
        valor_do_jogo_label.value = "Valor do jogo: R$ 0.00"
        
        page.update()  # Atualiza a página para refletir as mudanças

    def mostrar_listas_filtradas(e):
        try:
            numeros_escolhidos_string = tb4.value
            numeros_escolhidos = list(map(int, numeros_escolhidos_string.split(',')))

            if len(numeros_escolhidos) != 6:
                ft.popup("Erro", "Você deve escolher exatamente 6 números.")
                return

            listas_filtradas = []
            sena = 0
            quina = 0
            quadra = 0

            # Limpar a ListView antes de adicionar novas entradas
            lv.controls.clear()
            lv.controls.append(ft.Text("\nListas com os números escolhidos:\n"))

            for i, lista in enumerate(listas_geradas):
                correspondencias = [num for num in lista if num in numeros_escolhidos]
                if correspondencias:
                    if len(correspondencias) == 6:
                        sena += 1
                    elif len(correspondencias) == 5:
                        quina += 1
                    elif len(correspondencias) == 4:
                        quadra += 1
                
                    resultado_text = f"Lista {i + 1}: {lista}  \n--> Contém: {len(correspondencias)} ({', '.join(map(str, correspondencias))})\n"
                    if len(correspondencias) == 4:
                        lv.controls.append(ft.Text(resultado_text, color="blue"))  # Adicionar a nova lista à ListView
                    elif len(correspondencias) == 5:
                        lv.controls.append(ft.Text(resultado_text, color="green"))  # Adicionar a nova lista à ListView
                    elif len(correspondencias) == 6:
                        lv.controls.append(ft.Text(resultado_text, color="red"))  # Adicionar a nova lista à ListView

            # Atualiza os labels com os resultados
            label_sena.value = f"Sena: {sena}"
            label_quina.value = f"Quina: {quina}"
            label_quadra.value = f"Quadra: {quadra}"

            # Adiciona ao histórico
            historical_lv.controls.append(ft.Text(f"Sena: {sena}, Quina: {quina}, Quadra: {quadra}", size=20))

            page.update()  # Atualiza a página para refletir as mudanças na ListView

        except ValueError:
            ft.popup("Erro", "Por favor, insira valores válidos.")

    # Labels para resultados de Sena, Quina e Quadra
    label_sena = ft.Text("Sena: 0", size=30, color="pink600", italic=True)
    label_quina = ft.Text("Quina: 0", size=30, color="green500", italic=True)
    label_quadra = ft.Text("Quadra: 0", size=30, color="blue500", italic=True)

    # Criando containers para os resultados
    container_sena = ft.Container(content=label_sena, margin=10, alignment=ft.alignment.center)
    container_quina = ft.Container(content=label_quina, margin=10, alignment=ft.alignment.center)
    container_quadra = ft.Container(content=label_quadra, margin=10, alignment=ft.alignment.center)

    # Criando uma ListView para exibir os resultados com borda e altura limitada
    lv = ft.ListView(expand=1, spacing=10, padding=20, auto_scroll=True)
    lv_container = ft.Container(
        content=lv,
        margin=10,
        padding=10,
        border=ft.border.all(2, color=ft.colors.BLUE_600),  # Borda azul ao redor
        border_radius=10,
        height=400,  # Limite de altura
        width=550
    )

    

    label1 = ft.Text()
    tb1 = ft.TextField(
        label="Lista de números:",
        on_change=lambda e: label1.set_value(tb1.value),  # Atualiza o label1 com o valor do TextField
        width=610
    )

    label2 = ft.Text()
    tb2 = ft.TextField(
        label="Quantos jogos:",
        on_change=lambda e: label2.set_value(tb2.value)  # Atualiza o label2 com o valor do TextField
    )

    label3 = ft.Text()
    tb3 = ft.TextField(
        label="Quantos números em cada jogo?",
        on_change=lambda e: label3.set_value(tb3.value)
    )

    label4 = ft.Text()
    tb4 = ft.TextField(
        label="Escolha 6 simulando o jogo da mega",
        on_change=lambda e: label4.set_value(tb4.value),
        
    )

    button_valida_bilhete = ft.FilledButton(text="Filtra os bilhetes premiados", on_click=mostrar_listas_filtradas)
    button_gerar_jogo = ft.FilledButton(text="Gerar jogos", on_click=gerar)
    button_limpar_historico = ft.FilledButton(text="Limpar históricos", on_click=limpar)
    button_download = ft.FilledButton(text="Download das Listas", on_click=salvar_arquivo)
    button_download_historico = ft.FilledButton(
        text="Download historico",
        on_click=salvar_arquivo_historico
    )

    
    # Criando um ListView para o histórico de resultados com borda e altura limitada
    historical_lv = ft.ListView(expand=1, spacing=10, padding=20, auto_scroll=True)
    

    historical_lv_container = ft.Container(
        content=historical_lv,
        margin=10,
        padding=10,
        border=ft.border.all(2, color=ft.colors.GREEN_600),  # Borda verde ao redor
        border_radius=10,
        height=400  # Limite de altura
    )

    # Adicione isso na definição do layout
    historico = ft.Column(
        controls=[
            ft.Row(controls=[ft.Text("Histórico de Resultados", size=25, weight="bold")]),
            historical_lv_container,
            ft.Row(controls=[button_download_historico])
        ]
    )

    lista_de_jogos = ft.Column(
        controls=[
            ft.Row(controls=[ft.Text("Lista de jogos/Jogo premiados", size=25, weight="bold")]),
            lv_container,
            ft.Row(controls=[button_download])
        ] 
    )

    # Label para exibir o valor do jogo
    valor_do_jogo_label = ft.Text("Valor do jogo: R$ 0.00", size=20, color="black", italic=True)


    # Usando uma Column para organizar as linhas
    menu = ft.Column(
        controls=[
            ft.Row(controls=[label_sena,label_quina,label_quadra]),
            ft.Row(controls=[tb1]),  # Primeira linha com tb1
            ft.Row(controls=[tb2, tb3]),  # Segunda linha com tb2 e tb3
            ft.Row(controls=[tb4,button_valida_bilhete]),
            ft.Row(controls=[button_gerar_jogo,button_limpar_historico]),
            ft.Row(controls=[valor_do_jogo_label])
            ]
    )
       
    Geral = ft.Row(
        controls=[
            ft.Container(
                content=menu,  # Usando a propriedade correta
                margin=5,
                padding=10,
                alignment=ft.alignment.top_center,
                width=630,
                height=550,
                border_radius=2,
            ),
            ft.Container(
                content=lista_de_jogos,
                margin=10,
                padding=10,
                alignment=ft.alignment.center,
                width=450,
                height=550,
                border_radius=10,
                on_click=lambda e: print("Clickable without Ink clicked!"),
            ),
            ft.Container(
                content=historico,
                margin=10,
                padding=10,
                alignment=ft.alignment.center,
                width=450,
                height=550,
                border_radius=10,
                ink=True,
                on_click=lambda e: print("Clickable with Ink clicked!"),
            )
        ],
        alignment=ft.MainAxisAlignment.CENTER,
    )

    # Adicionando o Geral à página
    page.add(Geral)

# Iniciando o aplicativo
ft.app(target=main)
