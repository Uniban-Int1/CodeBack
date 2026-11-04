# 📊 MATRIZ DE CUMPLIMIENTO DE ENTREGABLES — EQUIPO 2

> **Proyecto Integrador Unibán** • *Backend & Modelos Predictivos / Deterministas • API FastAPI en Render*

---

### 📌 Resumen Ejecutivo de Cumplimiento

<table>
  <thead>
    <tr style="background-color: #f0f4f8;">
      <th align="center" width="25%">📦 Entregables Totales</th>
      <th align="center" width="25%">🎯 Cumplimiento</th>
      <th align="center" width="25%">🧪 Pruebas Automatizadas</th>
      <th align="center" width="25%">🚀 Arquitectura & Despliegue</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td align="center"><h3>10 de 10 Requerimientos</h3></td>
      <td align="center"><h3><span style="color: #2e7d32;">100%</span></h3></td>
      <td align="center"><h3>191 tests (100% OK)</h3></td>
      <td align="center"><h3>FastAPI en Render<br><small>Reglas D-001 a D-006</small></h3></td>
    </tr>
  </tbody>
</table>

---

## 📋 Matriz Detallada de Requerimientos y Evidencias Técnicas

<table>
  <thead>
    <tr style="background-color: #1b365d; color: #ffffff;">
      <th align="center" width="4%">#</th>
      <th align="left" width="24%">Requerimiento del Profesor</th>
      <th align="center" width="14%">Estado</th>
      <th align="left" width="28%">Dónde se encuentra en el Repositorio</th>
      <th align="left" width="30%">Descripción / Evidencia Técnica</th>
    </tr>
  </thead>
  <tbody>
    <!-- REQUERIMIENTO 1 -->
    <tr>
      <td align="center"><b>1</b></td>
      <td>
        <b>Modelo determinista completamente funcional y validado</b><br>
        <small>Cálculo de necesidades de cajas, cartón, bolsas y demás insumos.</small>
      </td>
      <td align="center">
        <b>✅ Cumplido (100%)</b>
      </td>
      <td>
        <ul>
          <li><b>Código núcleo:</b> <a href="https://github.com/Uniban-Int1/CodeBack/blob/develop-jose/app/core/insumos/estimacion.py" target="_blank" rel="noopener noreferrer"><code>app/core/insumos/estimacion.py</code></a></li>
          <li><b>Proyección base:</b> <a href="https://github.com/Uniban-Int1/CodeBack/blob/develop-jose/app/core/proyeccion/base.py" target="_blank" rel="noopener noreferrer"><code>app/core/proyeccion/base.py</code></a></li>
          <li><b>Parámetros:</b> <a href="https://github.com/Uniban-Int1/CodeBack/blob/develop-jose/config/parametros.yaml" target="_blank" rel="noopener noreferrer"><code>config/parametros.yaml</code></a></li>
          <li><b>Pruebas unitarias:</b> <a href="https://github.com/Uniban-Int1/CodeBack/blob/develop-jose/tests/casos/test_caso_03_estimacion_insumos.py" target="_blank" rel="noopener noreferrer"><code>test_caso_03_estimacion_insumos.py</code></a></li>
        </ul>
      </td>
      <td>
        Modela la cosecha semanal con la física del racimo (<code>1 / 10.5 semanas</code>). A partir del volumen proyectado, deriva cajas, cartón y bolsas con coeficientes técnicos configurables y calcula faltantes y excedentes. Validado con casos de prueba calculados a mano.
      </td>
    </tr>
    <!-- REQUERIMIENTO 2 -->
    <tr>
      <td align="center"><b>2</b></td>
      <td>
        <b>Modelo predictivo implementado y evaluado</b><br>
        <small>Métricas de error y comparación vs modelo base.</small>
      </td>
      <td align="center">
        <b>✅ Cumplido (100%)</b>
      </td>
      <td>
        <ul>
          <li><b>Código modelo:</b> <a href="https://github.com/Uniban-Int1/CodeBack/blob/develop-jose/app/core/proyeccion/predictivo.py" target="_blank" rel="noopener noreferrer"><code>app/core/proyeccion/predictivo.py</code></a></li>
          <li><b>Reporte técnico:</b> <a href="https://github.com/Uniban-Int1/CodeBack/blob/develop-jose/docs/reporte-evaluacion.md" target="_blank" rel="noopener noreferrer"><code>docs/reporte-evaluacion.md (§1 Resumen)</code></a></li>
          <li><b>Decisión D-003:</b> <a href="https://github.com/Uniban-Int1/CodeBack/blob/develop-jose/DECISIONES.md" target="_blank" rel="noopener noreferrer"><code>DECISIONES.md (Regla D-003)</code></a></li>
          <li><b>Pruebas:</b> <a href="https://github.com/Uniban-Int1/CodeBack/blob/develop-jose/tests/casos/test_caso_10_predictivo.py" target="_blank" rel="noopener noreferrer"><code>test_caso_10_predictivo.py</code></a></li>
        </ul>
      </td>
      <td>
        Implementado con <code>scikit-learn</code> y validación con partición temporal (<code>TimeSeriesSplit</code>). Compara Error MAE contra Línea Base Ingenua (18.4%), Modelo Determinista (7.2%) y Predictivo (8.1%). Aplica la regla <b>D-003</b> manteniendo el determinista en producción por ausencia de datos históricos de Unibán.
      </td>
    </tr>
    <!-- REQUERIMIENTO 3 -->
    <tr>
      <td align="center"><b>3</b></td>
      <td>
        <b>Módulo funcional de apoyo a la programación de cosecha y despacho</b><br>
        <small>Dentro del alcance comprometido.</small>
      </td>
      <td align="center">
        <b>✅ Cumplido (100%)</b>
      </td>
      <td>
        <ul>
          <li><b>Heurística:</b> <a href="https://github.com/Uniban-Int1/CodeBack/blob/develop-jose/app/core/programacion/heuristica.py" target="_blank" rel="noopener noreferrer"><code>app/core/programacion/heuristica.py</code></a></li>
          <li><b>Fechas límite:</b> <a href="https://github.com/Uniban-Int1/CodeBack/blob/develop-jose/app/core/programacion/fechas.py" target="_blank" rel="noopener noreferrer"><code>app/core/programacion/fechas.py</code></a></li>
          <li><b>Restricciones:</b> <a href="https://github.com/Uniban-Int1/CodeBack/blob/develop-jose/app/core/programacion/restricciones.py" target="_blank" rel="noopener noreferrer"><code>app/core/programacion/restricciones.py</code></a></li>
          <li><b>Pruebas:</b> <a href="https://github.com/Uniban-Int1/CodeBack/blob/develop-jose/tests/casos/test_caso_08_heuristica_programacion.py" target="_blank" rel="noopener noreferrer"><code>test_caso_08_heuristica_programacion.py</code></a></li>
        </ul>
      </td>
      <td>
        Algoritmo de 4 pasos que deduce la fecha de corte hacia atrás restando tiempos de empaque y acarreo desde la ventana de despacho fija, ordena parcelas por urgencia y asigna vehículos disponibles respetando capacidades máximas.
      </td>
    </tr>
    <!-- REQUERIMIENTO 4 -->
    <tr>
      <td align="center"><b>4</b></td>
      <td>
        <b>Capacidad de procesar aforamiento, cosecha, inventarios, consumos y ventanas</b><br>
        <small>Ingesta y validación de esquemas de datos.</small>
      </td>
      <td align="center">
        <b>✅ Cumplido (100%)</b>
      </td>
      <td>
        <ul>
          <li><b>Esquemas Ingesta:</b> <a href="https://github.com/Uniban-Int1/CodeBack/blob/develop-jose/app/schemas/ingesta.py" target="_blank" rel="noopener noreferrer"><code>app/schemas/ingesta.py</code></a></li>
          <li><b>Esquemas Recomendación:</b> <a href="https://github.com/Uniban-Int1/CodeBack/blob/develop-jose/app/schemas/recomendacion.py" target="_blank" rel="noopener noreferrer"><code>app/schemas/recomendacion.py</code></a></li>
          <li><b>Adaptador Equipo 3:</b> <a href="https://github.com/Uniban-Int1/CodeBack/blob/develop-jose/app/api/recomendacion.py" target="_blank" rel="noopener noreferrer"><code>app/api/recomendacion.py</code></a></li>
        </ul>
      </td>
      <td>
        Modelos Pydantic v2 con validación estricta que procesan <code>estimatedPlants</code>, <code>confidence</code>, <code>areaHa</code>, inventario (<code>inventory</code>), consumos, mermas/pérdidas y ventanas temporales con fecha/hora de inicio y fin.
      </td>
    </tr>
    <!-- REQUERIMIENTO 5 -->
    <tr>
      <td align="center"><b>5</b></td>
      <td>
        <b>Generación automática de recomendaciones de abastecimiento</b><br>
        <small>Cantidades requeridas, déficits o excedentes y fechas previstas.</small>
      </td>
      <td align="center">
        <b>✅ Cumplido (100%)</b>
      </td>
      <td>
        <ul>
          <li><b>Servicio central:</b> <a href="https://github.com/Uniban-Int1/CodeBack/blob/develop-jose/app/core/servicio.py" target="_blank" rel="noopener noreferrer"><code>app/core/servicio.py</code></a></li>
          <li><b>Pruebas unitarias:</b> <a href="https://github.com/Uniban-Int1/CodeBack/blob/develop-jose/tests/casos/test_caso_04_servicio.py" target="_blank" rel="noopener noreferrer"><code>test_caso_04_servicio.py</code></a></li>
          <li><b>Pruebas de excedentes:</b> <a href="https://github.com/Uniban-Int1/CodeBack/blob/develop-jose/tests/casos/test_caso_07_excedente_insumos.py" target="_blank" rel="noopener noreferrer"><code>test_caso_07_excedente_insumos.py</code></a></li>
        </ul>
      </td>
      <td>
        Función <code>recomendar_insumos()</code> que orquesta todo el flujo en memoria: calcula fecha límite de corte, racimos esperados y requerimiento exacto de insumos, determinando si hay déficit (<code>deficit &gt; 0</code>) o excedente en el inventario actual.
      </td>
    </tr>
    <!-- REQUERIMIENTO 6 -->
    <tr>
      <td align="center"><b>6</b></td>
      <td>
        <b>API funcional y documentada para recibir información del Equipo 3</b><br>
        <small>Recepción de entradas y retorno de recomendaciones.</small>
      </td>
      <td align="center">
        <b>✅ Cumplido (100%)</b>
      </td>
      <td>
        <ul>
          <li><b>Swagger UI (En vivo):</b> <a href="https://platano-logistica-api.onrender.com/docs" target="_blank" rel="noopener noreferrer"><code>platano-logistica-api.onrender.com/docs</code></a></li>
          <li><b>ReDoc:</b> <a href="https://platano-logistica-api.onrender.com/redoc" target="_blank" rel="noopener noreferrer"><code>platano-logistica-api.onrender.com/redoc</code></a></li>
          <li><b>Endpoint directo:</b> <a href="https://github.com/Uniban-Int1/CodeBack/blob/develop-jose/app/api/recomendacion.py" target="_blank" rel="noopener noreferrer"><code>app/api/recomendacion.py</code></a></li>
          <li><b>Endpoint ingesta:</b> <a href="https://github.com/Uniban-Int1/CodeBack/blob/develop-jose/app/api/ingesta.py" target="_blank" rel="noopener noreferrer"><code>app/api/ingesta.py</code></a></li>
          <li><b>Router principal:</b> <a href="https://github.com/Uniban-Int1/CodeBack/blob/develop-jose/app/main.py" target="_blank" rel="noopener noreferrer"><code>app/main.py</code></a></li>
        </ul>
      </td>
      <td>
        API REST en FastAPI desplegada en la nube en Render. Expone <code>POST /api/v1/recomendar</code>, <code>POST /api/v1/ingesta/operacion</code> y <code>GET /api/v1/planes/{periodo}</code>. Genera documentación interactiva OpenAPI disponible públicamente.
      </td>
    </tr>
    <!-- REQUERIMIENTO 7 -->
    <tr>
      <td align="center"><b>7</b></td>
      <td>
        <b>Evidencia de pruebas que permita establecer coherencia y trazabilidad</b><br>
        <small>Resultados auditables y consistentes.</small>
      </td>
      <td align="center">
        <b>✅ Cumplido (100%)</b>
      </td>
      <td>
        <ul>
          <li><b>Suite completa (191 tests):</b> <a href="https://github.com/Uniban-Int1/CodeBack/tree/develop-jose/tests" target="_blank" rel="noopener noreferrer"><code>tests/</code></a></li>
          <li><b>Pruebas API integración:</b> <a href="https://github.com/Uniban-Int1/CodeBack/blob/develop-jose/tests/test_api_recomendacion.py" target="_blank" rel="noopener noreferrer"><code>tests/test_api_recomendacion.py</code></a></li>
          <li><b>Trazabilidad D-005:</b> <a href="https://github.com/Uniban-Int1/CodeBack/blob/develop-jose/DECISIONES.md" target="_blank" rel="noopener noreferrer"><code>DECISIONES.md (Regla D-005)</code></a></li>
        </ul>
      </td>
      <td>
        191 pruebas automáticas pasando al 100% en <code>pytest</code>. Cada respuesta y plan incluye el campo obligatorio <code>version_metodo</code> (<code>determinista-v1</code>), permitiendo auditar la regla y el origen de cada recomendación.
      </td>
    </tr>
    <!-- REQUERIMIENTO 8 -->
    <tr>
      <td align="center"><b>8</b></td>
      <td>
        <b>Demostración obligatoria: Productor y parcela con variación de variables</b><br>
        <small>Modificación de variables de entrada y recálculo automático.</small>
      </td>
      <td align="center">
        <b>✅ Cumplido (100%)</b>
      </td>
      <td>
        <ul>
          <li><b>Script CLI interactivo:</b> <a href="https://github.com/Uniban-Int1/CodeBack/blob/develop-jose/scripts/demo_en_vivo.py" target="_blank" rel="noopener noreferrer"><code>scripts/demo_en_vivo.py</code></a></li>
          <li><b>Pestaña Simulador Móvil:</b> <a href="https://github.com/Uniban-Int1/CodeBack/blob/develop-jose/frontend/App.js" target="_blank" rel="noopener noreferrer"><code>frontend/App.js</code></a></li>
        </ul>
      </td>
      <td>
        Script ejecutable en consola (<code>python3 scripts/demo_en_vivo.py</code>) y simulador interactivo en la app móvil. Ejecutan el caso de la parcela <b>P-018</b> y permiten variar en tiempo real la ventana de despacho o el stock de cajas, mostrando el recálculo inmediato.
      </td>
    </tr>
    <!-- REQUERIMIENTO 9 -->
    <tr>
      <td align="center"><b>9</b></td>
      <td>
        <b>Recepción y visualización mediante el componente del Equipo 3</b><br>
        <small>Integración de extremo a extremo.</small>
      </td>
      <td align="center">
        <b>✅ Cumplido (100%)</b>
      </td>
      <td>
        <ul>
          <li><b>Endpoint en la nube:</b> <a href="https://platano-logistica-api.onrender.com/api/v1/recomendar" target="_blank" rel="noopener noreferrer"><code>POST /api/v1/recomendar</code></a></li>
          <li><b>Adaptador y normalizador:</b> <a href="https://github.com/Uniban-Int1/CodeBack/blob/develop-jose/app/api/recomendacion.py" target="_blank" rel="noopener noreferrer"><code>app/api/recomendacion.py</code></a></li>
          <li><b>Contrato acordado:</b> <a href="https://github.com/Uniban-Int1/CodeBack/blob/develop-jose/docs/contrato-integracion.md" target="_blank" rel="noopener noreferrer"><code>docs/contrato-integracion.md</code></a></li>
        </ul>
      </td>
      <td>
        El endpoint acepta el JSON exacto de la app móvil del Equipo 3 (IDs en UUID, ciclo activo y lista de inventario), y devuelve el objeto JSON con la hora límite de corte y el déficit de cajas/bolsas para que el Equipo 3 lo pinte en su pantalla.
      </td>
    </tr>
    <!-- REQUERIMIENTO 10 -->
    <tr>
      <td align="center"><b>10</b></td>
      <td>
        <b>Identificación y diferenciación explícita de datos simulados</b><br>
        <small>Transparencia técnica sin falsas validaciones reales.</small>
      </td>
      <td align="center">
        <b>✅ Cumplido (100%)</b>
      </td>
      <td>
        <ul>
          <li><b>Registro de Decisiones:</b> <a href="https://github.com/Uniban-Int1/CodeBack/blob/develop-jose/DECISIONES.md" target="_blank" rel="noopener noreferrer"><code>DECISIONES.md (Regla D-006)</code></a></li>
          <li><b>Reporte técnico:</b> <a href="https://github.com/Uniban-Int1/CodeBack/blob/develop-jose/docs/reporte-evaluacion.md" target="_blank" rel="noopener noreferrer"><code>docs/reporte-evaluacion.md</code></a></li>
          <li><b>Fixtures y pruebas:</b> <a href="https://github.com/Uniban-Int1/CodeBack/blob/develop-jose/tests/casos/test_caso_02_proyeccion_determinista.py" target="_blank" rel="noopener noreferrer"><code>test_caso_02_proyeccion_determinista.py</code></a></li>
        </ul>
      </td>
      <td>
        Cumplimiento formal de la regla <b>D-006</b>: como Unibán no ha entregado registros históricos reales, todos los datos simulados llevan el prefijo <code>sintetico_</code> y se declaran explícitamente en el código y reportes, sin presentarlos falsamente como validación real de campo.
      </td>
    </tr>
  </tbody>
</table>

---

## 🔗 Enlaces Directos y Repositorio de Evidencias (GitHub & Cloud)

<table>
  <thead>
    <tr style="background-color: #1b365d; color: #ffffff;">
      <th align="center" width="5%">#</th>
      <th align="left" width="30%">Recurso / Entregable</th>
      <th align="left" width="25%">Categoría / Tipo</th>
      <th align="left" width="40%">Acceso Directo (Hipervínculo Web)</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td align="center"><b>1</b></td>
      <td><b>Swagger API en Producción</b></td>
      <td>API Docs (OpenAPI / Cloud)</td>
      <td>🌐 <a href="https://platano-logistica-api.onrender.com/docs" target="_blank" rel="noopener noreferrer"><code>https://platano-logistica-api.onrender.com/docs</code></a></td>
    </tr>
    <tr>
      <td align="center"><b>2</b></td>
      <td><b>Endpoint de Integración POST /recomendar</b></td>
      <td>API REST Endpoint</td>
      <td>🌐 <a href="https://platano-logistica-api.onrender.com/api/v1/recomendar" target="_blank" rel="noopener noreferrer"><code>https://platano-logistica-api.onrender.com/api/v1/recomendar</code></a></td>
    </tr>
    <tr>
      <td align="center"><b>3</b></td>
      <td><b>Contrato de Integración con Equipo 3</b></td>
      <td>Especificación Técnica</td>
      <td>📄 <a href="https://github.com/Uniban-Int1/CodeBack/blob/develop-jose/docs/contrato-integracion.md" target="_blank" rel="noopener noreferrer"><code>docs/contrato-integracion.md</code></a></td>
    </tr>
    <tr>
      <td align="center"><b>4</b></td>
      <td><b>Registro de Decisiones (D-001 a D-006)</b></td>
      <td>Decisiones de Arquitectura (ADR)</td>
      <td>📄 <a href="https://github.com/Uniban-Int1/CodeBack/blob/develop-jose/DECISIONES.md" target="_blank" rel="noopener noreferrer"><code>DECISIONES.md</code></a></td>
    </tr>
    <tr>
      <td align="center"><b>5</b></td>
      <td><b>Reporte Técnico de Evaluación de Modelos</b></td>
      <td>Métricas &amp; Error MAE</td>
      <td>📄 <a href="https://github.com/Uniban-Int1/CodeBack/blob/develop-jose/docs/reporte-evaluacion.md" target="_blank" rel="noopener noreferrer"><code>docs/reporte-evaluacion.md</code></a></td>
    </tr>
    <tr>
      <td align="center"><b>6</b></td>
      <td><b>Script de Demostración en Vivo</b></td>
      <td>Script CLI (Python)</td>
      <td>🐍 <a href="https://github.com/Uniban-Int1/CodeBack/blob/develop-jose/scripts/demo_en_vivo.py" target="_blank" rel="noopener noreferrer"><code>scripts/demo_en_vivo.py</code></a></td>
    </tr>
    <tr>
      <td align="center"><b>7</b></td>
      <td><b>Lógica de Insumos y Fechas de Cosecha</b></td>
      <td>Servicio Central (Core)</td>
      <td>⚙️ <a href="https://github.com/Uniban-Int1/CodeBack/blob/develop-jose/app/core/servicio.py" target="_blank" rel="noopener noreferrer"><code>app/core/servicio.py</code></a></td>
    </tr>
    <tr>
      <td align="center"><b>8</b></td>
      <td><b>Repositorio Completo GitHub (develop-jose)</b></td>
      <td>Control de Versiones</td>
      <td>🐙 <a href="https://github.com/Uniban-Int1/CodeBack/tree/develop-jose" target="_blank" rel="noopener noreferrer"><code>GitHub: Uniban-Int1/CodeBack</code></a></td>
    </tr>
  </tbody>
</table>
