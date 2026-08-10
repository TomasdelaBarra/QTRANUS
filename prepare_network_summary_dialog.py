from qgis.PyQt.QtWidgets import QDialog, QVBoxLayout, QTextBrowser
from qgis.PyQt.QtCore import Qt
from qgis.utils import iface


class PrepareNetworkSummaryDialog(QDialog):
    def __init__(self, parent=None, added_links=None, removed_links=None, final_links=None, added_nodes=None):
        super().__init__(parent)
        self.setWindowTitle("Network Processing Summary")
        self.resize(600, 500)
        self.added_links = added_links if added_links is not None else 0
        self.removed_links = removed_links if removed_links is not None else 0
        self.final_links = final_links if final_links is not None else 0
        self.added_nodes = added_nodes if added_nodes is not None else 0

        # 1. Aseguramos explícitamente que la ventana NO sea modal
        self.setModal(False)
        
        # Configurar el diseño
        layout = QVBoxLayout(self)
        
        # 2. Crear un QTextBrowser para renderizar el HTML
        self.text_browser = QTextBrowser(self)
        self.text_browser.setOpenExternalLinks(True) # Permite abrir enlaces en el navegador web
        
        # 3. Definir y cargar tu contenido HTML
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
        <style>
        body { font-family: sans-serif; margin: 15px; color: #333; }
        .grid { display: flex; gap: 15px; margin-bottom: 20px; }
        .grid {
            width: 100%;
            border-collapse: separate;
            border-spacing: 15px 0;
            margin-bottom: 20px;
            table-layout: fixed;
        }
        .card { flex: 1; padding: 15px; border-radius: 6px; text-align: center; border: 1px solid #ddd; }
        .card-cell { width: 33.33%; vertical-align: top; padding: 0; border: none; }
        .card {
            padding: 15px;
            border-radius: 6px;
            text-align: center;
            border: 1px solid #ddd;
        }
        .card.added { background-color: #ebf7ee; border-color: #badcc3; }
        .card.removed { background-color: #fdf2f2; border-color: #f3cad0; }
        .card.total { background-color: #f0f7fc; border-color: #b7dbf1; }
        .number { font-size: 24px; font-weight: bold; display: block; margin-top: 5px; }
        .added .number { color: #27ae60; }
        .removed .number { color: #c0392b; }
        .total .number { color: #2980b9; }
        
        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th, td { text-align: left; padding: 8px; border-bottom: 1px solid #ddd; }
        th { background-color: #f5f5f5; font-size: 13px; }
        .badge { background: #e0e0e0; padding: 2px 6px; border-radius: 4px; font-size: 11px; }
        .badge-model { background: #d4edda; color: #155724; }
        .badge-required { background: #FFA591; color: #FF3105; }
        </style>
        </head>
        <body>

        <h3>Network Processing Summary</h3>
        <p>The network layer has been successfully adapted for the transport model.</p>

        <!-- KPI Cards para Geometría -->
        <table class="grid">
            <tr>
                <td class="card-cell">
                    <div class="card added">
                        <span>Links Added</span>
                        <span class="number">+""" + str(self.added_links) + """</span>
                    </div>
                </td>
                <td class="card-cell">
                    <div class="card removed">
                        <span>Links Removed</span>
                        <span class="number">-""" + str(self.removed_links) + """</span>
                    </div>
                </td>
                <td class="card-cell">
                    <div class="card total">
                        <span>Final Links</span>
                        <span class="number">""" + str(self.final_links) + """</span>
                    </div>
                </td>
                <td class="card-cell">
                    <div class="card added">
                        <span>Nodes Added</span>
                        <br>
                        <span class="number">+""" + str(self.added_nodes) + """</span>
                    </div>
                </td>
            </tr>
        </table>

        <!-- Tabla de Atributos -->
        <h3>Attributes Schema</h3>
        <table>
            <tr>
            <th>Field Name</th>
            <th>Type</th>
            <th>Origin</th>
            </tr>
            <tr>
            <td><code>Origin</code></td>
            <td>Integer64</td>
            <td><span class="badge">Optional</span></td>
            </tr>
            <tr>
            <td><code>Destination</code></td>
            <td>Integer64</td>
            <td><span class="badge">Optional</span></td>
            </tr>
            <tr>
            <td><code>LinkID</code></td>
            <td>Integer64</td>
            <td><span class="badge">String</span></td>
            </tr>
            <tr>
            <td><code>Length</code></td>
            <td>Double</td>
            <td><span class="badge">Optional</span></td>
            </tr>
            <tr>
            <td><code>Name</code></td>
            <td>String</td>
            <td><span class="badge">Optional</span></td>
            </tr>
            <tr>
            <td><code>Type</code></td>
            <td>String</td>
            <td><span class="badge">Optional</span></td>
            </tr>
            <tr>
            <td><code>Direction</code></td>
            <td>Integer</td>
            <td><span class="badge badge-required">Required</span></td>
            </tr>
            <tr>
            <td><code>Capacity</code></td>
            <td>Integer</td>
            <td><span class="badge">Optional</span></td>
            </tr>
        </table>
        </body>
        </html>         
        """
        
        self.text_browser.setHtml(html_content)
        layout.addWidget(self.text_browser)

