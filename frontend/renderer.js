const { ipcRenderer } = require('electron');

// Exemplo de botão no HTML: <button id="separateBtn">Separar Track</button>
document.getElementById('separateBtn').addEventListener('click', async () => {
  try {
    const result = await ipcRenderer.invoke('separate-track');
    if (result.success) {
      alert(`Instrumental salvo em: ${result.output_file}`);
    } else {
      alert(`Erro: ${result.error}`);
    }
  } catch (err) {
    alert(`Falha: ${err.message}`);
  }
});