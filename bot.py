from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    page.goto("https://web.whatsapp.com")

    print("Escaneie o QR Code se necessário")
    time.sleep(15)  # tempo para login

    print("Bot iniciado. Aguardando mensagens...")

    while True:
        try:
            # pega a conversa ativa
            chats = page.query_selector_all("div[role='row']")

            for chat in chats[:1]:  # só o primeiro (conversa aberta)
                chat.click()
                time.sleep(1)

                # pega a última mensagem recebida
                mensagens = page.query_selector_all("div.message-in span.selectable-text")
                if mensagens:
                    texto = mensagens[-1].inner_text()
                    print("Mensagem recebida:", texto)

                    # caixa de texto
                    caixa = page.query_selector("div[contenteditable='true']")
                    if caixa:
                        caixa.fill("Olá! Sou o bot do consultório 😊")
                        caixa.press("Enter")
                        time.sleep(2)

        except Exception as e:
            print("Erro:", e)

        time.sleep(5)
