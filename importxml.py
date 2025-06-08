import xml.etree.ElementTree as ET
import tkinter as tk
from tkinter import filedialog, messagebox

class NFEEditor:
    def __init__(self, master):
        self.master = master
        master.title("Editor de XML da NFe, criado por joseph, email:josephsantiago250@gmail.com")
        master.geometry("700x600")

        self.ns = {'nfe': 'http://www.portalfiscal.inf.br/nfe'}
        ET.register_namespace('', self.ns['nfe'])

        self.tree = None
        self.produtos = []

        # Botão abrir XML
        self.btn_abrir = tk.Button(master, text="Abrir XML", command=self.abrir_xml)
        self.btn_abrir.pack()

        # Lista de produtos
        self.lista = tk.Listbox(master)
        self.lista.pack(fill=tk.BOTH, expand=True)
        self.lista.bind('<<ListboxSelect>>', self.mostrar_detalhes)

        # Frame com Scroll para edição
        self.frame_scroll = tk.Frame(master)
        self.frame_scroll.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.frame_scroll)
        self.scrollbar = tk.Scrollbar(self.frame_scroll, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Campos básicos do produto
        self.campos = {}
        campos_basicos = ['descricao', 'quantidade', 'valor_unitario', 'valor_total']
        for campo in campos_basicos:
            label = tk.Label(self.scrollable_frame, text=campo.capitalize())
            label.pack()
            entry = tk.Entry(self.scrollable_frame)
            entry.pack(fill=tk.X)
            self.campos[campo] = entry

        # Campos para ICMS
        tk.Label(self.scrollable_frame, text="--- ICMS ---").pack(pady=(10,0))
        self.icms_campos = {}
        icms_campos = ['orig', 'CST', 'modBC', 'vBC', 'pICMS', 'vICMS']
        for campo in icms_campos:
            label = tk.Label(self.scrollable_frame, text=f"ICMS {campo}")
            label.pack()
            entry = tk.Entry(self.scrollable_frame)
            entry.pack(fill=tk.X)
            self.icms_campos[campo] = entry

        # Campos para IPI
        tk.Label(self.scrollable_frame, text="--- IPI ---").pack(pady=(10,0))
        self.ipi_campos = {}
        ipi_campos = ['CST', 'vBC', 'pIPI', 'vIPI']
        for campo in ipi_campos:
            label = tk.Label(self.scrollable_frame, text=f"IPI {campo}")
            label.pack()
            entry = tk.Entry(self.scrollable_frame)
            entry.pack(fill=tk.X)
            self.ipi_campos[campo] = entry

        # Botões para salvar
        self.btn_salvar = tk.Button(master, text="Salvar Alterações", command=self.salvar_alteracoes)
        self.btn_salvar.pack(pady=5)

        self.btn_salvar_xml = tk.Button(master, text="Salvar XML Editado", command=self.salvar_xml)
        self.btn_salvar_xml.pack(pady=5)

    def abrir_xml(self):
        caminho = filedialog.askopenfilename(filetypes=[("Arquivo XML", "*.xml")])
        if not caminho:
            return

        self.tree = ET.parse(caminho)
        root = self.tree.getroot()
        self.produtos = []

        self.lista.delete(0, tk.END)

        for det in root.findall('.//nfe:det', self.ns):
            prod = det.find('nfe:prod', self.ns)
            imposto = det.find('nfe:imposto', self.ns)

            icms = None
            ipi = None

            if imposto is not None:
                icms = imposto.find('.//nfe:ICMS', self.ns)
                ipi = imposto.find('.//nfe:IPI', self.ns)

            produto = {
                'elemento': prod,
                'imposto_elemento': imposto,
                'icms_elemento': icms,
                'ipi_elemento': ipi,
                'codigo': prod.findtext('nfe:cProd', '', self.ns),
                'descricao': prod.findtext('nfe:xProd', '', self.ns),
                'quantidade': prod.findtext('nfe:qCom', '', self.ns),
                'valor_unitario': prod.findtext('nfe:vUnCom', '', self.ns),
                'valor_total': prod.findtext('nfe:vProd', '', self.ns),
                'icms': {},
                'ipi': {}
            }

            # Preenche dados ICMS
            if icms is not None:
                for icms_tipo in icms:
                    for campo in self.icms_campos.keys():
                        elem = icms_tipo.find(f"nfe:{campo}", self.ns)
                        if elem is not None:
                            produto['icms'][campo] = elem.text
                        else:
                            produto['icms'][campo] = ''
                    break

            # Preenche dados IPI
            if ipi is not None:
                ipi_trib = ipi.find('nfe:IPITrib', self.ns)
                if ipi_trib is not None:
                    for campo in self.ipi_campos.keys():
                        elem = ipi_trib.find(f"nfe:{campo}", self.ns)
                        if elem is not None:
                            produto['ipi'][campo] = elem.text
                        else:
                            produto['ipi'][campo] = ''
                else:
                    for campo in self.ipi_campos.keys():
                        produto['ipi'][campo] = ''

            self.produtos.append(produto)
            self.lista.insert(tk.END, f"{produto['descricao']}")

    def mostrar_detalhes(self, event):
        selecionado = self.lista.curselection()
        if not selecionado:
            return
        idx = selecionado[0]
        produto = self.produtos[idx]

        self.campos['descricao'].delete(0, tk.END)
        self.campos['descricao'].insert(0, produto['descricao'])
        self.campos['quantidade'].delete(0, tk.END)
        self.campos['quantidade'].insert(0, produto['quantidade'])
        self.campos['valor_unitario'].delete(0, tk.END)
        self.campos['valor_unitario'].insert(0, produto['valor_unitario'])
        self.campos['valor_total'].delete(0, tk.END)
        self.campos['valor_total'].insert(0, produto['valor_total'])

        for campo, entry in self.icms_campos.items():
            entry.delete(0, tk.END)
            entry.insert(0, produto['icms'].get(campo, ''))

        for campo, entry in self.ipi_campos.items():
            entry.delete(0, tk.END)
            entry.insert(0, produto['ipi'].get(campo, ''))

    def salvar_alteracoes(self):
        selecionado = self.lista.curselection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione um produto para editar.")
            return
        idx = selecionado[0]
        produto = self.produtos[idx]

        produto['descricao'] = self.campos['descricao'].get()
        produto['quantidade'] = self.campos['quantidade'].get()
        produto['valor_unitario'] = self.campos['valor_unitario'].get()
        produto['valor_total'] = self.campos['valor_total'].get()

        prod_element = produto['elemento']
        prod_element.find('nfe:xProd', self.ns).text = produto['descricao']
        prod_element.find('nfe:qCom', self.ns).text = produto['quantidade']
        prod_element.find('nfe:vUnCom', self.ns).text = produto['valor_unitario']
        prod_element.find('nfe:vProd', self.ns).text = produto['valor_total']

        icms_element = produto['icms_elemento']
        if icms_element is not None:
            for icms_tipo in icms_element:
                for campo, entry in self.icms_campos.items():
                    elem = icms_tipo.find(f"nfe:{campo}", self.ns)
                    if elem is not None:
                        elem.text = entry.get()
                break

        ipi_element = produto['ipi_elemento']
        if ipi_element is not None:
            ipi_trib = ipi_element.find('nfe:IPITrib', self.ns)
            if ipi_trib is not None:
                for campo, entry in self.ipi_campos.items():
                    elem = ipi_trib.find(f"nfe:{campo}", self.ns)
                    if elem is not None:
                        elem.text = entry.get()

        self.lista.delete(idx)
        self.lista.insert(idx, produto['descricao'])
        messagebox.showinfo("Sucesso", "Produto e impostos atualizados com sucesso.")

    def salvar_xml(self):
        if not self.tree:
            messagebox.showerror("Erro", "Nenhum XML carregado.")
            return
        caminho = filedialog.asksaveasfilename(defaultextension=".xml", filetypes=[("Arquivo XML", "*.xml")])
        if caminho:
            self.tree.write(caminho, encoding='utf-8', xml_declaration=True)
            messagebox.showinfo("Salvo", f"XML salvo em: {caminho}")

if __name__ == "__main__":
    root = tk.Tk()
    app = NFEEditor(root)
    root.mainloop()
