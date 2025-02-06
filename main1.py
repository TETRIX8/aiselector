import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import json
import threading
import time
import requests
from ttkthemes import ThemedTk  # Импортируем ThemedTk для стилизации

class SelectorFinder:
    def __init__(self, root):
        self.root = root
        self.root.title("A-K Project: Поиск селекторов элементов с ИИ")  # Название проекта
        self.driver = None
        self.current_element = None
        self.selectors = {}
        
        self.setup_ui()
        self.start_browser()

    def setup_ui(self):
        """Настройка интерфейса"""
        # Устанавливаем тему для стилизации
        self.root.set_theme("arc")  # Вы можете выбрать другую тему, например "plastik", "clearlooks" и т.д.

        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Кнопки управления
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=5)
        
        self.btn_pick = ttk.Button(
            control_frame, 
            text="Выбрать элемент", 
            command=self.start_element_picking,
            style="Accent.TButton"  # Используем стиль для кнопки
        )
        self.btn_pick.pack(side=tk.LEFT, padx=5)

        self.btn_save = ttk.Button(
            control_frame, 
            text="Сохранить селектор", 
            command=self.save_selector,
            state=tk.DISABLED,
            style="Accent.TButton"  # Используем стиль для кнопки
        )
        self.btn_save.pack(side=tk.LEFT, padx=5)

        # Информационные панели
        info_panel = ttk.Notebook(main_frame)
        
        # Вкладка с селектором
        selector_tab = ttk.Frame(info_panel)
        self.selector_info = tk.Text(
            selector_tab, 
            height=8, 
            wrap=tk.WORD,
            state=tk.DISABLED,
            font=("Arial", 10)  # Устанавливаем шрифт
        )
        self.selector_info.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Вкладка с содержимым
        content_tab = ttk.Frame(info_panel)
        self.element_content = tk.Text(
            content_tab, 
            height=8, 
            wrap=tk.WORD,
            state=tk.DISABLED,
            font=("Arial", 10)  # Устанавливаем шрифт
        )
        self.element_content.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Вкладка с объяснением ИИ
        ai_tab = ttk.Frame(info_panel)
        self.ai_explanation = tk.Text(
            ai_tab, 
            height=8, 
            wrap=tk.WORD,
            state=tk.DISABLED,
            font=("Arial", 10)  # Устанавливаем шрифт
        )
        self.ai_explanation.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        info_panel.add(selector_tab, text="Селектор")
        info_panel.add(content_tab, text="Содержимое")
        info_panel.add(ai_tab, text="Объяснение ИИ")
        info_panel.pack(fill=tk.BOTH, expand=True, pady=10)

        # Статус бар
        self.status_bar = ttk.Label(
            main_frame, 
            text="Статус: Готово",
            relief=tk.SUNKEN,
            font=("Arial", 10)  # Устанавливаем шрифт
        )
        self.status_bar.pack(fill=tk.X)

    def start_browser(self):
        """Запуск браузера"""
        chrome_options = Options()
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--start-maximized")
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(
            service=service, 
            options=chrome_options
        )
        self.driver.get("https://www.emersonecologics.com/onboarding")

    def update_status(self, message):
        """Обновление статус бара"""
        self.status_bar.config(text=f"Статус: {message}")
        self.root.update()

    def start_element_picking(self):
        """Начать выбор элемента"""
        self.update_status("Выберите элемент на странице...")
        self.btn_save.config(state=tk.DISABLED)
        self.driver.execute_script("""
            document.body.style.cursor = 'crosshair';
            window.enablePicker = true;
            
            document.addEventListener('mouseover', function(e) {
                if(window.enablePicker) {
                    e.target.style.outline = '2px solid red';
                }
            });
            
            document.addEventListener('mouseout', function(e) {
                if(window.enablePicker) {
                    e.target.style.outline = '';
                }
            });
            
            document.addEventListener('click', function(e) {
                if(window.enablePicker) {
                    e.preventDefault();
                    window.enablePicker = false;
                    document.body.style.cursor = 'default';
                    e.target.style.outline = '';
                    window.selectedElement = e.target;
                }
            });
        """)
        threading.Thread(target=self.wait_for_element).start()

    def wait_for_element(self):
        """Ожидание выбора элемента"""
        while True:
            element = self.driver.execute_script("return window.selectedElement;")
            if element:
                self.process_selected_element(element)
                break
            self.root.update()
            time.sleep(0.1)

    def process_selected_element(self, element):
        """Обработка выбранного элемента"""
        self.current_element = element
        selector = self.generate_selector(element)
        content = self.get_element_content(element)
        
        self.selector_info.config(state=tk.NORMAL)
        self.selector_info.delete(1.0, tk.END)
        self.selector_info.insert(tk.END, selector)
        self.selector_info.config(state=tk.DISABLED)
        
        self.element_content.config(state=tk.NORMAL)
        self.element_content.delete(1.0, tk.END)
        self.element_content.insert(tk.END, content)
        self.element_content.config(state=tk.DISABLED)
        
        self.btn_save.config(state=tk.NORMAL)
        self.update_status("Элемент выбран")

    def generate_selector(self, element):
        """Генерация CSS-селектора"""
        attributes = self.driver.execute_script(
            "var items = {}; " 
            "var attrs = arguments[0].attributes; " 
            "for (var i = 0; i < attrs.length; i++) { " 
            "  items[attrs[i].name] = attrs[i].value; " 
            "} " 
            "return items;", 
            element
        )
        
        if attributes.get('id'):
            return f"#{attributes['id']}"
        
        if attributes.get('class'):
            classes = attributes['class'].split()
            for cls in classes:
                if not cls.isdigit():
                    return f".{cls}"
        
        for attr in ['name', 'href', 'src', 'aria-label']:
            if attributes.get(attr):
                return f"[{attr}='{attributes[attr]}']"
        
        return self.driver.execute_script(
            "function getPath(element) {" 
            "  if (element.tagName === 'HTML') return '/HTML';" 
            "  if (element === document.body) return '/HTML/BODY';" 
            "  var index = 0;" 
            "  var siblings = element.parentNode.childNodes;" 
            "  for (var i = 0; i < siblings.length; i++) {" 
            "    if (siblings[i] === element) return getPath(element.parentNode) + '/' + element.tagName + '[' + (index + 1) + ']';" 
            "    if (siblings[i].nodeType === 1 && siblings[i].tagName === element.tagName) index++;" 
            "  }" 
            "}" 
            "return getPath(arguments[0]);", 
            element
        )

    def get_element_content(self, element):
        """Получение содержимого элемента"""
        content = self.driver.execute_script(
            "return arguments[0].outerHTML || arguments[0].textContent;", 
            element
        )
        return content.strip() if content else "N/A"

    def save_selector(self):
        """Сохранение селектора с объяснением ИИ"""
        element_name = simpledialog.askstring(
            "Сохранение", 
            "Введите название элемента:"
        )
        if element_name:
            selector = self.selector_info.get(1.0, tk.END).strip()
            content = self.element_content.get(1.0, tk.END).strip()
            
            self.selectors[element_name] = {
                "selector": selector,
                "content": content,
                "ai_explanation": "Загрузка..."
            }
            
            threading.Thread(
                target=self.process_ai_explanation,
                args=(element_name, selector, content)
            ).start()
            
            messagebox.showinfo("Информация", "Начата генерация объяснения ИИ...")

    def process_ai_explanation(self, element_name, selector, content):
        """Обработка объяснения от ИИ в отдельном потоке"""
        explanation = self.get_ai_explanation(selector, content)
        self.selectors[element_name]["ai_explanation"] = explanation
        
        with open("selectors.json", "w") as f:
            json.dump(self.selectors, f, indent=2)
        
        self.root.after(0, self.update_explanation_ui, explanation)

    def get_ai_explanation(self, selector, content):
        """Получение объяснения от ИИ"""
        prompt = (
            f"Объясни на русском языке:\n"
            f"1. Тип элемента и его назначение по этому селектору: {selector}\n"
            f"2. Как правильно парсить содержимое: {content[:200]}...\n"
            f"3. Потенциальные проблемы при парсинге\n"
            f"Форматируй ответ с нумерованным списком"
        )
        
        try:
            payload = {
                "messages": [{"role": "user", "content": prompt}],
                "web_access": False
            }
            
            headers = {
                'x-rapidapi-key': '7de6f5a7edmsh00119ac6a48dc9fp100bedjsn0e63adf77f99',
                'x-rapidapi-host': 'chatgpt-42.p.rapidapi.com',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(
                'https://chatgpt-42.p.rapidapi.com/gpt4',
                json=payload,
                headers=headers,
                timeout=15
            )
            
            if response.status_code == 200:
                return response.json().get("result", "Объяснение недоступно")
            return f"Ошибка API: {response.status_code}"
        
        except Exception as e:
            return f"Ошибка: {str(e)}"

    def update_explanation_ui(self, explanation):
        """Обновление интерфейса с объяснением"""
        self.ai_explanation.config(state=tk.NORMAL)
        self.ai_explanation.delete(1.0, tk.END)
        self.ai_explanation.insert(tk.END, explanation)
        self.ai_explanation.config(state=tk.DISABLED)
        messagebox.showinfo("Готово", "Данные успешно сохранены!")

    def on_close(self):
        """Закрытие приложения"""
        if messagebox.askokcancel("Выход", "Закрыть программу?"):
            self.driver.quit()
            self.root.destroy()

if __name__ == "__main__":
    root = ThemedTk(theme="arc")  # Используем ThemedTk для стилизации
    app = SelectorFinder(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
