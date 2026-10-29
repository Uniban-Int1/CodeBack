import React, { useState, useEffect } from 'react';
import {
  StyleSheet,
  Text,
  View,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  SafeAreaView,
  RefreshControl,
  TextInput,
} from 'react-native';
import { StatusBar } from 'expo-status-bar';

// Backend desplegado en Render (plan free: la primera llamada tras inactividad
// puede tardar ~90 s en responder mientras el servicio despierta).
const API_BASE_URL = 'https://platano-logistica-api.onrender.com';

// Semana ISO 8601 con el formato del contrato, p. ej. "2026-W44".
const semanaIso = (fecha) => {
  const d = new Date(Date.UTC(fecha.getFullYear(), fecha.getMonth(), fecha.getDate()));
  const diaSemana = d.getUTCDay() || 7;
  d.setUTCDate(d.getUTCDate() + 4 - diaSemana);
  const inicioAnio = new Date(Date.UTC(d.getUTCFullYear(), 0, 1));
  const semana = Math.ceil(((d - inicioAnio) / 86400000 + 1) / 7);
  return `${d.getUTCFullYear()}-W${String(semana).padStart(2, '0')}`;
};

const PLAN_DEMO = {
  plan_id: "PL-2026-W38",
  periodo: "2026-W38",
  version_metodo: "heuristica-v1",
  generado_en: new Date().toISOString(),
  metricas: {
    cumplimiento_ventana: 0.92,
    uso_capacidad: 0.85,
  },
  items: [
    {
      parcela_id: "P-018",
      fecha_corte: "2026-09-20 06:00",
      vehiculo_id: "V-3",
      orden: 1,
      carga_estimada_racimos: 210,
      cumple_ventana: true,
      motivo: null,
    },
    {
      parcela_id: "P-022",
      fecha_corte: "2026-09-20 07:30",
      vehiculo_id: "V-3",
      orden: 2,
      carga_estimada_racimos: 190,
      cumple_ventana: true,
      motivo: null,
    },
    {
      parcela_id: "P-031",
      fecha_corte: "2026-09-21 14:00",
      vehiculo_id: "—",
      orden: 3,
      carga_estimada_racimos: 150,
      cumple_ventana: false,
      motivo: "excede_capacidad_vehiculos",
    },
  ],
  insumos: [
    {
      insumo: "cajas",
      fecha: "2026-09-20",
      cantidad_requerida: 340,
      inventario_disponible: 250,
      deficit: 90,
    },
    {
      insumo: "carton",
      fecha: "2026-09-20",
      cantidad_requerida: 340,
      inventario_disponible: 400,
      deficit: 0,
    },
    {
      insumo: "bolsas",
      fecha: "2026-09-20",
      cantidad_requerida: 400,
      inventario_disponible: 350,
      deficit: 50,
    },
  ],
};

export default function App() {
  const [seccion, setSeccion] = useState('recoleccion'); // 'recoleccion' | 'insumos' | 'simulador' | 'modelos'
  const [periodo, setPeriodo] = useState('2026-W38');
  const [cargando, setCargando] = useState(true);
  const [refrescando, setRefrescando] = useState(false);
  const [plan, setPlan] = useState(PLAN_DEMO);
  const [fuente, setFuente] = useState('cargando');

  // Estado del Simulador en Vivo (para la demostración de sustentación)
  const [simPlantas, setSimPlantas] = useState('1850');
  const [simArea, setSimArea] = useState('2.4');
  const [simInventarioCajas, setSimInventarioCajas] = useState('300');
  const [simVentanaFin, setSimVentanaFin] = useState('16:00'); // Hora de fin de despacho
  const [simResultado, setSimResultado] = useState(null);
  const [simCalculando, setSimCalculando] = useState(false);
  const [evaluacion, setEvaluacion] = useState(null);
  const [evalCargando, setEvalCargando] = useState(false);
  const [evalError, setEvalError] = useState(false);

  // Métricas calculadas en el backend (escenario sintético declarado), nunca valores fijos.
  const cargarEvaluacion = async () => {
    setEvalCargando(true);
    setEvalError(false);
    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/modelos/evaluacion`, {
        headers: { Accept: 'application/json' },
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      setEvaluacion(await res.json());
    } catch (err) {
      setEvalError(true);
    } finally {
      setEvalCargando(false);
    }
  };

  // Respaldo local con la misma fórmula del backend, por si Render no responde.
  const calcularLocal = () => {
    const numPlantas = parseFloat(simPlantas) || 0;
    const invCajas = parseFloat(simInventarioCajas) || 0;
    const cicloSemanas = 10.5;
    const confianza = 0.87;
    const factorPerdida = 0.05;

    // Fórmula determinista oficial:
    // volumen = num_plantas * (1 / ciclo) * confianza * (1 - factor_perdida)
    const racimosEsperados = Math.round(
      numPlantas * (1 / cicloSemanas) * confianza * (1 - factorPerdida)
    );

    // Coeficiente consumo: cajas = 0.85 por racimo
    const cajasRequeridas = Math.round(racimosEsperados * 0.85);
    const deficitCajas = Math.max(0, cajasRequeridas - invCajas);
    const excedenteCajas = Math.max(0, invCajas - cajasRequeridas);

    // Cálculo de fecha límite hacia atrás:
    // fecha_limite = ventana_fin - 120min (empaque) - 35min (acarreo) - 30min (margen) = -185min (~3h 05min)
    const [horas, mins] = simVentanaFin.split(':').map(Number);
    const totalMinutos = (horas || 16) * 60 + (mins || 0) - 185;
    const horaLimite = Math.floor(Math.max(0, totalMinutos) / 60);
    const minLimite = Math.max(0, totalMinutos) % 60;
    const horaLimiteStr = `${horaLimite.toString().padStart(2, '0')}:${minLimite.toString().padStart(2, '0')}`;

    return {
      racimosEsperados,
      cajasRequeridas,
      invCajas,
      deficitCajas,
      excedenteCajas,
      horaLimiteStr,
      cumpleVentana: totalMinutos >= 6 * 60, // Si cabe después de las 06:00
      fuenteSim: 'local',
    };
  };

  // Llama al POST /api/v1/recomendar real en Render. La ventana de despacho se fija
  // mañana (06:00 a la hora indicada) para no recomendar sobre una fecha ya pasada.
  const ejecutarSimulacion = async () => {
    setSimCalculando(true);
    const manana = new Date();
    manana.setDate(manana.getDate() + 1);
    const dia = `${manana.getFullYear()}-${String(manana.getMonth() + 1).padStart(2, '0')}-${String(manana.getDate()).padStart(2, '0')}`;
    const [h, m] = simVentanaFin.split(':').map(Number);
    const finStr = `${String(h || 16).padStart(2, '0')}:${String(m || 0).padStart(2, '0')}:00`;

    const cuerpo = {
      parcela_id: 'P-DEMO',
      periodo: semanaIso(manana),
      num_plantas_estimado: parseInt(simPlantas, 10) || 0,
      calidad_confianza: 0.87,
      area_ha: parseFloat(simArea) || 2.4,
      inventario: {
        cajas: parseFloat(simInventarioCajas) || 0,
        carton: 400,
        bolsas: 350,
      },
      ventana_despacho: { inicio: `${dia}T06:00:00`, fin: `${dia}T${finStr}` },
    };

    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/recomendar`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify(cuerpo),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      const cajas = data.insumos.find((i) => i.insumo === 'cajas') || {};
      setSimResultado({
        racimosEsperados: data.volumen_racimos,
        cajasRequeridas: cajas.cantidad_requerida,
        invCajas: cajas.inventario_disponible,
        deficitCajas: cajas.deficit,
        excedenteCajas: cajas.excedente ?? 0,
        horaLimiteStr: data.fecha_limite_corte.slice(11, 16),
        cumpleVentana: data.cumple_ventana,
        fuenteSim: 'render',
      });
    } catch (err) {
      setSimResultado(calcularLocal());
    } finally {
      setSimCalculando(false);
    }
  };

  const cargarDatos = async () => {
    try {
      setCargando(true);
      const res = await fetch(`${API_BASE_URL}/api/v1/planes/${periodo}`, {
        headers: { Accept: 'application/json' },
      });
      if (res.ok) {
        const data = await res.json();
        setPlan(data);
        setFuente('api_en_vivo');
      } else {
        setPlan(PLAN_DEMO);
        setFuente('modo_demostracion');
      }
    } catch (err) {
      setPlan(PLAN_DEMO);
      setFuente('sin_conexion_demo');
    } finally {
      setCargando(false);
      setRefrescando(false);
    }
  };

  useEffect(() => {
    cargarDatos();
    ejecutarSimulacion();
  }, [periodo]);

  const onRefresh = () => {
    setRefrescando(true);
    cargarDatos();
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <StatusBar style="light" />
      {/* Header */}
      <View style={styles.header}>
        <View style={styles.badgeBanner}>
          <Text style={styles.badgeBannerText}>UNIBÁN · URABÁ</Text>
        </View>
        <Text style={styles.titulo}>Plátano Logística</Text>
        <Text style={styles.subtitulo}>Planificación de Cosecha & Empaque</Text>

        {/* Selector de Periodo */}
        <View style={styles.periodoSelectorRow}>
          <Text style={styles.selectorLabel}>Semana:</Text>
          {['2026-W37', '2026-W38', '2026-W39'].map((sem) => (
            <TouchableOpacity
              key={sem}
              style={[styles.chipSemana, periodo === sem && styles.chipSemanaActiva]}
              onPress={() => setPeriodo(sem)}
            >
              <Text
                style={[styles.chipSemanaTexto, periodo === sem && styles.chipSemanaTextoActivo]}
              >
                {sem.replace('2026-', '')}
              </Text>
            </TouchableOpacity>
          ))}
        </View>

        {fuente !== 'api_en_vivo' && (seccion === 'recoleccion' || seccion === 'insumos') && (
          <View style={styles.alertaOffline}>
            <Text style={styles.alertaOfflineText}>
              ℹ️ Plan de ejemplo: aún no hay planes guardados en el backend ({fuente})
            </Text>
          </View>
        )}
      </View>

      {/* Tabs / Barra de Navegación */}
      <View style={styles.tabContainer}>
        <TouchableOpacity
          style={[styles.tab, seccion === 'recoleccion' && styles.tabActivo]}
          onPress={() => setSeccion('recoleccion')}
        >
          <Text style={[styles.tabTexto, seccion === 'recoleccion' && styles.tabTextoActivo]}>
            🚛 Recolección
          </Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[styles.tab, seccion === 'insumos' && styles.tabActivo]}
          onPress={() => setSeccion('insumos')}
        >
          <Text style={[styles.tabTexto, seccion === 'insumos' && styles.tabTextoActivo]}>
            📦 Insumos
          </Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[styles.tab, seccion === 'simulador' && styles.tabActivo]}
          onPress={() => setSeccion('simulador')}
        >
          <Text style={[styles.tabTexto, seccion === 'simulador' && styles.tabTextoActivo]}>
            🧪 Simulador
          </Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[styles.tab, seccion === 'modelos' && styles.tabActivo]}
          onPress={() => setSeccion('modelos')}
        >
          <Text style={[styles.tabTexto, seccion === 'modelos' && styles.tabTextoActivo]}>
            📈 Modelos
          </Text>
        </TouchableOpacity>
      </View>

      {/* Contenido según sección */}
      <ScrollView
        contentContainerStyle={styles.scrollContent}
        refreshControl={<RefreshControl refreshing={refrescando} onRefresh={onRefresh} />}
      >
        {cargando && !refrescando ? (
          <View style={styles.loaderContainer}>
            <ActivityIndicator size="large" color="#1F5C3A" />
            <Text style={styles.loaderTexto}>Cargando datos del sistema...</Text>
          </View>
        ) : seccion === 'recoleccion' ? (
          /* --- SECCIÓN 1: RECOLECCIÓN --- */
          <View>
            {plan.metricas && (
              <View style={styles.kpiContainer}>
                <View style={styles.kpiCard}>
                  <Text style={styles.kpiValor}>
                    {Math.round(plan.metricas.cumplimiento_ventana * 100)}%
                  </Text>
                  <Text style={styles.kpiLabel}>Cumplimiento Ventana</Text>
                </View>
                <View style={styles.kpiCard}>
                  <Text style={styles.kpiValor}>
                    {Math.round(plan.metricas.uso_capacidad * 100)}%
                  </Text>
                  <Text style={styles.kpiLabel}>Uso de Capacidad</Text>
                </View>
              </View>
            )}

            <Text style={styles.seccionTitulo}>Secuencia de Corte y Transporte</Text>
            {plan.items?.map((item, index) => (
              <View
                key={index}
                style={[
                  styles.card,
                  item.cumple_ventana ? styles.cardOk : styles.cardRiesgo,
                ]}
              >
                <View style={styles.cardHeader}>
                  <View style={styles.tagOrden}>
                    <Text style={styles.tagOrdenText}>#{item.orden}</Text>
                  </View>
                  <Text style={styles.parcelaId}>Parcela {item.parcela_id}</Text>
                  <View
                    style={[
                      styles.tagEstado,
                      item.cumple_ventana ? styles.tagOk : styles.tagRiesgo,
                    ]}
                  >
                    <Text
                      style={[
                        styles.tagEstadoTexto,
                        item.cumple_ventana ? styles.tagEstadoOkTexto : styles.tagEstadoRiesgoTexto,
                      ]}
                    >
                      {item.cumple_ventana ? '✓ Cumple Ventana' : '✕ Alerta'}
                    </Text>
                  </View>
                </View>

                <View style={styles.cardBody}>
                  <Text style={styles.cardText}>
                    🕒 <Text style={styles.bold}>Corte Límite:</Text> {item.fecha_corte}
                  </Text>
                  <Text style={styles.cardText}>
                    🚚 <Text style={styles.bold}>Vehículo Asignado:</Text> {item.vehiculo_id || 'Sin asignar'}
                  </Text>
                  <Text style={styles.cardText}>
                    🍌 <Text style={styles.bold}>Carga Estimada:</Text> {item.carga_estimada_racimos} racimos
                  </Text>
                  {item.motivo && (
                    <Text style={styles.motivoAlerta}>Motivo: {item.motivo}</Text>
                  )}
                </View>
              </View>
            ))}
          </View>
        ) : seccion === 'insumos' ? (
          /* --- SECCIÓN 2: INSUMOS --- */
          <View>
            <Text style={styles.seccionTitulo}>Requerimientos de Empaque</Text>
            {plan.insumos?.map((insumo, index) => (
              <View
                key={index}
                style={[
                  styles.card,
                  insumo.deficit > 0 ? styles.cardRiesgo : styles.cardOk,
                ]}
              >
                <View style={styles.cardHeader}>
                  <Text style={styles.insumoNombre}>{insumo.insumo.toUpperCase()}</Text>
                  {insumo.deficit > 0 ? (
                    <View style={styles.tagRiesgo}>
                      <Text style={styles.tagEstadoRiesgoTexto}>Déficit: {insumo.deficit}</Text>
                    </View>
                  ) : (
                    <View style={styles.tagOk}>
                      <Text style={styles.tagEstadoOkTexto}>Stock Completo</Text>
                    </View>
                  )}
                </View>

                <View style={styles.cardBody}>
                  <View style={styles.insumoGrid}>
                    <View style={styles.insumoCol}>
                      <Text style={styles.insumoColLabel}>Requerido</Text>
                      <Text style={styles.insumoColVal}>{insumo.cantidad_requerida}</Text>
                    </View>
                    <View style={styles.insumoCol}>
                      <Text style={styles.insumoColLabel}>Inventario</Text>
                      <Text style={styles.insumoColVal}>{insumo.inventario_disponible}</Text>
                    </View>
                    <View style={styles.insumoCol}>
                      <Text style={styles.insumoColLabel}>Faltante</Text>
                      <Text style={[styles.insumoColVal, insumo.deficit > 0 && styles.deficitVal]}>
                        {insumo.deficit}
                      </Text>
                    </View>
                  </View>
                </View>
              </View>
            ))}
          </View>
        ) : seccion === 'simulador' ? (
          /* --- SECCIÓN 3: SIMULADOR EN VIVO (Demostración obligatoria) --- */
          <View>
            <View style={styles.bannerSimulador}>
              <Text style={styles.bannerSimuladorTitulo}>🧪 Demostración en Vivo</Text>
              <Text style={styles.bannerSimuladorDesc}>
                Modifica las variables de entrada para evidenciar el cambio automático en la fecha límite de corte y déficit de empaque.
              </Text>
            </View>

            <View style={styles.formCard}>
              <Text style={styles.formGroupLabel}>Conteo de Plantas Aforadas:</Text>
              <TextInput
                style={styles.input}
                keyboardType="numeric"
                value={simPlantas}
                onChangeText={(val) => {
                  setSimPlantas(val);
                }}
              />

              <Text style={styles.formGroupLabel}>Inventario de Cajas en Acopio:</Text>
              <TextInput
                style={styles.input}
                keyboardType="numeric"
                value={simInventarioCajas}
                onChangeText={(val) => {
                  setSimInventarioCajas(val);
                }}
              />

              <Text style={styles.formGroupLabel}>Hora Fin Ventana de Despacho (HH:MM):</Text>
              <TextInput
                style={styles.input}
                value={simVentanaFin}
                placeholder="16:00"
                onChangeText={(val) => {
                  setSimVentanaFin(val);
                }}
              />

              <TouchableOpacity
                style={styles.btnSimular}
                onPress={ejecutarSimulacion}
                disabled={simCalculando}
              >
                <Text style={styles.btnSimularTexto}>
                  {simCalculando ? 'Consultando el backend en Render...' : '⚡ Recalcular Recomendación'}
                </Text>
              </TouchableOpacity>
            </View>

            {simResultado && (
              <View style={styles.resultadoCard}>
                <Text style={styles.resultadoTitulo}>📊 Salida del Algoritmo</Text>
                <Text style={styles.resLabel}>
                  {simResultado.fuenteSim === 'render'
                    ? 'Fuente: backend en vivo (Render, POST /api/v1/recomendar)'
                    : 'Fuente: cálculo local (Render no respondió)'}
                </Text>

                <View style={styles.resultadoFila}>
                  <Text style={styles.resLabel}>Cosecha Esperada:</Text>
                  <Text style={styles.resValor}>{simResultado.racimosEsperados} racimos</Text>
                </View>

                <View style={styles.resultadoFila}>
                  <Text style={styles.resLabel}>Hora Límite de Corte:</Text>
                  <Text style={[styles.resValor, styles.resValorDestacado]}>
                    {simResultado.horaLimiteStr} hrs
                  </Text>
                </View>

                <View style={styles.resultadoFila}>
                  <Text style={styles.resLabel}>Cajas Requeridas:</Text>
                  <Text style={styles.resValor}>{simResultado.cajasRequeridas} cajas</Text>
                </View>

                <View style={styles.resultadoFila}>
                  <Text style={styles.resLabel}>Estado del Déficit:</Text>
                  <Text
                    style={[
                      styles.resValor,
                      simResultado.deficitCajas > 0 ? styles.deficitVal : styles.tagEstadoOkTexto,
                    ]}
                  >
                    {simResultado.deficitCajas > 0
                      ? `⚠️ Déficit de ${simResultado.deficitCajas} cajas`
                      : `✓ Abastecido (Sobra: ${simResultado.excedenteCajas})`}
                  </Text>
                </View>

                <View
                  style={[
                    styles.tagResultadoVentana,
                    simResultado.cumpleVentana ? styles.tagOk : styles.tagRiesgo,
                  ]}
                >
                  <Text
                    style={[
                      styles.tagEstadoTexto,
                      simResultado.cumpleVentana
                        ? styles.tagEstadoOkTexto
                        : styles.tagEstadoRiesgoTexto,
                    ]}
                  >
                    {simResultado.cumpleVentana
                      ? '✓ La fruta llega a tiempo al embarque'
                      : '✕ Ventana inalcanzable (retrasar acarreo)'}
                  </Text>
                </View>
              </View>
            )}
          </View>
        ) : (
          /* --- SECCIÓN 4: MODELOS Y COMPARATIVA DE ERROR --- */
          <View>
            <View style={styles.card}>
              <Text style={styles.modeloTitulo}>📈 Evaluación y Comparación de Modelos</Text>
              <Text style={styles.modeloDesc}>
                Regla D-003: El modelo predictivo solo reemplaza al determinista si supera a la línea base ingenua y al modelo base.
              </Text>

              <TouchableOpacity style={styles.btnSimular} onPress={cargarEvaluacion} disabled={evalCargando}>
                <Text style={styles.btnSimularTexto}>
                  {evalCargando ? 'Evaluando en Render...' : '📊 Correr evaluación en el backend'}
                </Text>
              </TouchableOpacity>

              {evalError && (
                <Text style={styles.resLabel}>
                  No se pudo obtener la evaluación desde Render. Vuelve a intentar en unos segundos.
                </Text>
              )}

              {evaluacion && (
                <View>
                  <Text style={styles.resLabel}>⚠️ {evaluacion.advertencia}</Text>
                  <Text style={styles.resLabel}>MAE en {evaluacion.unidad} (menor es mejor)</Text>

                  {/* Tabla calculada por GET /api/v1/modelos/evaluacion */}
                  <View style={styles.tablaModelos}>
                    <View style={styles.tablaHeader}>
                      <Text style={[styles.th, { flex: 1 }]}>Bloque</Text>
                      <Text style={[styles.th, { flex: 1 }]}>Predictivo</Text>
                      <Text style={[styles.th, { flex: 1 }]}>Determinista</Text>
                      <Text style={[styles.th, { flex: 1 }]}>Ingenua</Text>
                    </View>
                    {[...evaluacion.bloques, evaluacion.holdout].map((b) => (
                      <View
                        key={b.bloque}
                        style={[styles.tablaFila, b.bloque === 'holdout' && styles.filaOficial]}
                      >
                        <Text style={[styles.td, { flex: 1 }, b.bloque === 'holdout' && styles.bold]}>
                          {b.bloque}
                        </Text>
                        <Text style={[styles.td, { flex: 1 }]}>{b.mae_predictivo.toFixed(2)}</Text>
                        <Text style={[styles.td, { flex: 1 }]}>{b.mae_determinista.toFixed(2)}</Text>
                        <Text style={[styles.td, { flex: 1 }]}>{b.mae_ingenua.toFixed(2)}</Text>
                      </View>
                    ))}
                  </View>

                  <View style={styles.notaAcademica}>
                    <Text style={styles.notaAcademicaTitulo}>📋 Decisión D-003 (sobre el holdout)</Text>
                    <Text style={styles.notaAcademicaTexto}>{evaluacion.decision_d003.texto}</Text>
                  </View>
                </View>
              )}
            </View>
          </View>
        )}
      </ScrollView>

      {/* Footer */}
      <View style={styles.footer}>
        <Text style={styles.footerTexto}>Proyecto Integrador I · Grupo 7 · UdeA 2026-2</Text>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: '#1F5C3A',
  },
  header: {
    backgroundColor: '#1F5C3A',
    paddingHorizontal: 16,
    paddingTop: 12,
    paddingBottom: 14,
  },
  badgeBanner: {
    alignSelf: 'flex-start',
    backgroundColor: '#144028',
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 4,
    marginBottom: 4,
  },
  badgeBannerText: {
    color: '#A3D9B1',
    fontSize: 10,
    fontWeight: '700',
    letterSpacing: 0.8,
  },
  titulo: {
    color: '#FFFFFF',
    fontSize: 22,
    fontWeight: '800',
  },
  subtitulo: {
    color: '#D4E8DC',
    fontSize: 12,
    marginTop: 2,
  },
  periodoSelectorRow: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#174A2E',
    borderRadius: 8,
    paddingHorizontal: 10,
    paddingVertical: 6,
    marginTop: 10,
  },
  selectorLabel: {
    color: '#E0EFE6',
    fontSize: 12,
    fontWeight: '600',
    marginRight: 8,
  },
  chipSemana: {
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 6,
    backgroundColor: 'rgba(255,255,255,0.1)',
    marginRight: 6,
  },
  chipSemanaActiva: {
    backgroundColor: '#FFFFFF',
  },
  chipSemanaTexto: {
    color: '#E0EFE6',
    fontSize: 12,
    fontWeight: '600',
  },
  chipSemanaTextoActivo: {
    color: '#1F5C3A',
    fontWeight: '800',
  },
  alertaOffline: {
    backgroundColor: '#FFF3CD',
    borderRadius: 6,
    padding: 6,
    marginTop: 8,
  },
  alertaOfflineText: {
    color: '#856404',
    fontSize: 11,
    textAlign: 'center',
  },
  tabContainer: {
    flexDirection: 'row',
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#E2E8F0',
  },
  tab: {
    flex: 1,
    paddingVertical: 12,
    alignItems: 'center',
    borderBottomWidth: 3,
    borderBottomColor: 'transparent',
  },
  tabActivo: {
    borderBottomColor: '#1F5C3A',
  },
  tabTexto: {
    fontSize: 12,
    fontWeight: '600',
    color: '#64748B',
  },
  tabTextoActivo: {
    color: '#1F5C3A',
    fontWeight: '800',
  },
  scrollContent: {
    padding: 14,
    backgroundColor: '#F1F4EE',
    flexGrow: 1,
  },
  loaderContainer: {
    marginTop: 60,
    alignItems: 'center',
  },
  loaderTexto: {
    marginTop: 12,
    color: '#1F5C3A',
    fontSize: 14,
  },
  kpiContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 14,
  },
  kpiCard: {
    flex: 0.48,
    backgroundColor: '#FFFFFF',
    padding: 12,
    borderRadius: 10,
    alignItems: 'center',
    elevation: 2,
    shadowColor: '#000',
    shadowOpacity: 0.05,
    shadowRadius: 4,
  },
  kpiValor: {
    fontSize: 22,
    fontWeight: '800',
    color: '#1F5C3A',
  },
  kpiLabel: {
    fontSize: 11,
    color: '#64748B',
    marginTop: 4,
    textAlign: 'center',
  },
  seccionTitulo: {
    fontSize: 15,
    fontWeight: '700',
    color: '#14201A',
    marginBottom: 10,
  },
  card: {
    backgroundColor: '#FFFFFF',
    borderRadius: 10,
    padding: 14,
    marginBottom: 12,
    borderLeftWidth: 5,
    elevation: 2,
    shadowColor: '#000',
    shadowOpacity: 0.05,
    shadowRadius: 4,
  },
  cardOk: {
    borderLeftColor: '#1F5C3A',
  },
  cardRiesgo: {
    borderLeftColor: '#A8452B',
    backgroundColor: '#FFF7F5',
  },
  cardHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  tagOrden: {
    backgroundColor: '#E2E8F0',
    borderRadius: 12,
    paddingHorizontal: 8,
    paddingVertical: 2,
    marginRight: 8,
  },
  tagOrdenText: {
    fontSize: 11,
    fontWeight: '700',
    color: '#334155',
  },
  parcelaId: {
    fontSize: 15,
    fontWeight: '700',
    color: '#1E293B',
    flex: 1,
  },
  tagEstado: {
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 6,
  },
  tagOk: {
    backgroundColor: '#D1E7DD',
  },
  tagRiesgo: {
    backgroundColor: '#F8D7DA',
  },
  tagEstadoTexto: {
    fontSize: 11,
    fontWeight: '700',
  },
  tagEstadoOkTexto: {
    color: '#0F5132',
  },
  tagEstadoRiesgoTexto: {
    color: '#842029',
  },
  cardBody: {
    gap: 4,
  },
  cardText: {
    fontSize: 13,
    color: '#334155',
  },
  bold: {
    fontWeight: '700',
  },
  motivoAlerta: {
    fontSize: 11,
    color: '#A8452B',
    fontWeight: '600',
    marginTop: 4,
  },
  insumoNombre: {
    fontSize: 15,
    fontWeight: '800',
    color: '#1E293B',
    flex: 1,
  },
  insumoGrid: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    backgroundColor: '#F8FAFC',
    borderRadius: 8,
    padding: 10,
    marginTop: 6,
  },
  insumoCol: {
    alignItems: 'center',
    flex: 1,
  },
  insumoColLabel: {
    fontSize: 10,
    color: '#64748B',
    marginBottom: 2,
  },
  insumoColVal: {
    fontSize: 15,
    fontWeight: '700',
    color: '#1E293B',
  },
  deficitVal: {
    color: '#A8452B',
    fontWeight: '700',
  },
  /* Estilos Simulador */
  bannerSimulador: {
    backgroundColor: '#E8F5E9',
    borderRadius: 8,
    padding: 12,
    marginBottom: 12,
    borderLeftWidth: 4,
    borderLeftColor: '#1F5C3A',
  },
  bannerSimuladorTitulo: {
    fontSize: 15,
    fontWeight: '700',
    color: '#1F5C3A',
    marginBottom: 4,
  },
  bannerSimuladorDesc: {
    fontSize: 12,
    color: '#2E7D32',
    lineHeight: 16,
  },
  formCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 10,
    padding: 14,
    marginBottom: 14,
  },
  formGroupLabel: {
    fontSize: 12,
    fontWeight: '600',
    color: '#475569',
    marginBottom: 4,
    marginTop: 6,
  },
  input: {
    backgroundColor: '#F8FAFC',
    borderWidth: 1,
    borderColor: '#CBD5E1',
    borderRadius: 6,
    paddingHorizontal: 10,
    paddingVertical: 8,
    fontSize: 14,
    color: '#1E293B',
  },
  btnSimular: {
    backgroundColor: '#1F5C3A',
    borderRadius: 8,
    paddingVertical: 12,
    alignItems: 'center',
    marginTop: 14,
  },
  btnSimularTexto: {
    color: '#FFFFFF',
    fontSize: 14,
    fontWeight: '700',
  },
  resultadoCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 10,
    padding: 14,
    borderWidth: 1,
    borderColor: '#E2E8F0',
  },
  resultadoTitulo: {
    fontSize: 14,
    fontWeight: '800',
    color: '#1E293B',
    marginBottom: 10,
  },
  resultadoFila: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 6,
    borderBottomWidth: 1,
    borderBottomColor: '#F1F5F9',
  },
  resLabel: {
    fontSize: 13,
    color: '#64748B',
  },
  resValor: {
    fontSize: 13,
    fontWeight: '600',
    color: '#1E293B',
  },
  resValorDestacado: {
    color: '#1F5C3A',
    fontWeight: '800',
  },
  tagResultadoVentana: {
    marginTop: 12,
    paddingVertical: 8,
    borderRadius: 6,
    alignItems: 'center',
  },
  /* Estilos Modelos */
  modeloTitulo: {
    fontSize: 16,
    fontWeight: '800',
    color: '#1E293B',
    marginBottom: 4,
  },
  modeloDesc: {
    fontSize: 12,
    color: '#64748B',
    lineHeight: 16,
    marginBottom: 12,
  },
  tablaModelos: {
    backgroundColor: '#F8FAFC',
    borderRadius: 8,
    overflow: 'hidden',
    marginBottom: 12,
  },
  tablaHeader: {
    flexDirection: 'row',
    backgroundColor: '#E2E8F0',
    paddingVertical: 8,
    paddingHorizontal: 10,
  },
  th: {
    fontSize: 11,
    fontWeight: '700',
    color: '#334155',
  },
  tablaFila: {
    flexDirection: 'row',
    paddingVertical: 10,
    paddingHorizontal: 10,
    borderBottomWidth: 1,
    borderBottomColor: '#E2E8F0',
    alignItems: 'center',
  },
  filaOficial: {
    backgroundColor: '#EDF7ED',
  },
  td: {
    fontSize: 12,
    color: '#334155',
  },
  tdBadge: {
    fontSize: 11,
    fontWeight: '700',
  },
  notaAcademica: {
    backgroundColor: '#FEF9C3',
    borderRadius: 8,
    padding: 10,
    borderLeftWidth: 4,
    borderLeftColor: '#CA8A04',
  },
  notaAcademicaTitulo: {
    fontSize: 12,
    fontWeight: '700',
    color: '#854D0E',
    marginBottom: 2,
  },
  notaAcademicaTexto: {
    fontSize: 11,
    color: '#713F12',
    lineHeight: 15,
  },
  footer: {
    backgroundColor: '#FFFFFF',
    paddingVertical: 10,
    alignItems: 'center',
    borderTopWidth: 1,
    borderTopColor: '#E2E8F0',
  },
  footerTexto: {
    fontSize: 10,
    color: '#94A3B8',
  },
});
