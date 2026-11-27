# Comprueba el dashboard real del agregador con Playwright MCP

La ruta de favoritos puede verse correcta en el código mientras el dashboard muestra resultados obsoletos. Este laboratorio arranca la aplicación del artículo 0005, carga una base SQLite descartable y compara el navegador antes y después de recargar.

## Conecta las herramientas con alcance de proyecto

`.mcp.json` inicia el servidor oficial de Playwright MCP mediante `npx`. El ejemplo fija `0.0.86` y usa Chrome sin ventana con un perfil aislado. Revisa la aprobación del proyecto en Claude Code. Trabaja con la aplicación local y los datos de laboratorio.

## Observa la cuadrícula en lugar de toda la página

El resumen y la cuadrícula pueden contener los mismos títulos. Limita las comprobaciones de búsqueda a `#articlesGrid`. Busca `MCP no Agregador` y espera a que aparezca mientras `Roteamento no OpenCode` sale de la cuadrícula. Identifica el botón dentro de la tarjeta correcta.

## Comprueba una escritura y una lectura nueva

Marca el favorito y espera `Adicionado aos favoritos`. Comprueba `GET /favoritos`. Activa `⭐ Apenas Favoritos`, recarga, vuelve a activar el filtro y confirma que el artículo sigue en la vista. El filtro vuelve al estado inicial al recargar y el registro guardado permanece.

## Verifica la eliminación con un artículo de control

Quita el artículo objetivo mientras la vista está filtrada. Debe salir de la cuadrícula y `=Arquitetura, "em prática"` debe seguir como favorito de control. Comprueba la misma relación por HTTP. Cada paso cubre un detalle distinto, desde la confirmación visual hasta el estado persistido.

## Repite con el verificador directo

`verify_dashboard.py` usa el mismo servidor MCP y la aplicación de loopback. Espera el contenido de la cuadrícula y compara la lista JSON. Pide al agente paso, observación y evidencia. Convierte los recorridos estables en pruebas deterministas cuando necesites repetirlos con frecuencia.

[Lee el artículo completo](https://github.com/pathbit/pathbit-ai-for-devs/tree/master/0010_playwright_mcp_agregador/article/ARTICLE.es.md)

Developed with ❤️ by [Pathbit](https://pathbit.co/)
