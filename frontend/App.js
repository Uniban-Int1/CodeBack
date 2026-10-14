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
  Platform,
} from 'react-native';
import { StatusBar } from 'expo-status-bar';

// En emulador Android usar 10.0.2.2; en web o dispositivo físico usar localhost o la IP de tu red LAN
const API_BASE_URL = Platform.OS === 'android' ? 'http://10.0.2.2:8000' : 'http://localhost:8000';

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
  const [seccion, setSeccion] = useState('recoleccion'); // 'recoleccion' | 'insumos'
  const [periodo, setPeriodo] = useState('2026-W38');
  const [cargando, setCargando] = useState(true);
  const [refrescando, setRefrescando] = useState(false);
  const [plan, setPlan] = useState(PLAN_DEMO);
  const [fuente, setFuente] = useState('cargando');

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
        // Fallback demo si el periodo aún no está en la base de datos
        setPlan(PLAN_DEMO);
        setFuente('modo_demostracion');
      }
    } catch (err) {
      // Si la API no está disponible o hay fallo de red
      setPlan(PLAN_DEMO);
      setFuente('sin_conexion_demo');
    } finally {
      setCargando(false);
      setRefrescando(false);
    }
  };

  useEffect(() => {
    cargarDatos();
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
        <Text style={styles.subtitulo}>Planificación de Recolección e Insumos</Text>
        
        {/* Barra de periodo y método */}
        <View style={styles.metaRow}>
          <Text style={styles.metaItem}>📅 Semana: <Text style={styles.bold}>{plan.periodo}</Text></Text>
          <Text style={styles.metaItem}>⚙️ Método: <Text style={styles.bold}>{plan.version_metodo}</Text></Text>
        </View>

        {fuente !== 'api_en_vivo' && (
          <View style={styles.alertaOffline}>
            <Text style={styles.alertaOfflineText}>
              ℹ️ Mostrando datos de demostración (API {API_BASE_URL} no detectada)
            </Text>
          </View>
        )}
      </View>

      {/* Tabs */}
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
            📦 Insumos & Déficit
          </Text>
        </TouchableOpacity>
      </View>

      {/* Contenido Principal */}
      <ScrollView
        contentContainerStyle={styles.scrollContent}
        refreshControl={<RefreshControl refreshing={refrescando} onRefresh={onRefresh} />}
      >
        {cargando && !refrescando ? (
          <View style={styles.loaderContainer}>
            <ActivityIndicator size="large" color="#1F5C3A" />
            <Text style={styles.loaderTexto}>Cargando plan...</Text>
          </View>
        ) : seccion === 'recoleccion' ? (
          <View>
            {/* Tarjeta de Métricas */}
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

            <Text style={styles.seccionTitulo}>Secuencia de Acarreo y Despacho</Text>
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
                      {item.cumple_ventana ? '✓ Cumple' : '✕ Alerta'}
                    </Text>
                  </View>
                </View>

                <View style={styles.cardBody}>
                  <Text style={styles.cardText}>
                    🕒 <Text style={styles.bold}>Corte Límite:</Text> {item.fecha_corte}
                  </Text>
                  <Text style={styles.cardText}>
                    🚚 <Text style={styles.bold}>Vehículo:</Text> {item.vehiculo_id || 'Sin asignar'}
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
        ) : (
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
                  <Text style={styles.insumoNombre}>
                    {insumo.insumo.toUpperCase()}
                  </Text>
                  {insumo.deficit > 0 ? (
                    <View style={styles.tagRiesgo}>
                      <Text style={styles.tagEstadoRiesgoTexto}>
                        Déficit: {insumo.deficit}
                      </Text>
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
    paddingHorizontal: 20,
    paddingTop: 16,
    paddingBottom: 16,
  },
  badgeBanner: {
    alignSelf: 'flex-start',
    backgroundColor: '#144028',
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 4,
    marginBottom: 6,
  },
  badgeBannerText: {
    color: '#A3D9B1',
    fontSize: 11,
    fontWeight: '700',
    letterSpacing: 0.8,
  },
  titulo: {
    color: '#FFFFFF',
    fontSize: 24,
    fontWeight: '800',
  },
  subtitulo: {
    color: '#D4E8DC',
    fontSize: 13,
    marginTop: 2,
  },
  metaRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    backgroundColor: '#174A2E',
    borderRadius: 8,
    padding: 10,
    marginTop: 12,
  },
  metaItem: {
    color: '#E0EFE6',
    fontSize: 13,
  },
  bold: {
    fontWeight: '700',
  },
  alertaOffline: {
    backgroundColor: '#FFF3CD',
    borderRadius: 6,
    padding: 8,
    marginTop: 10,
  },
  alertaOfflineText: {
    color: '#856404',
    fontSize: 12,
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
    paddingVertical: 14,
    alignItems: 'center',
    borderBottomWidth: 3,
    borderBottomColor: 'transparent',
  },
  tabActivo: {
    borderBottomColor: '#1F5C3A',
  },
  tabTexto: {
    fontSize: 15,
    fontWeight: '600',
    color: '#64748B',
  },
  tabTextoActivo: {
    color: '#1F5C3A',
    fontWeight: '700',
  },
  scrollContent: {
    padding: 16,
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
    fontSize: 15,
  },
  kpiContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 16,
  },
  kpiCard: {
    flex: 0.48,
    backgroundColor: '#FFFFFF',
    padding: 14,
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
    fontSize: 12,
    color: '#64748B',
    marginTop: 4,
    textAlign: 'center',
  },
  seccionTitulo: {
    fontSize: 16,
    fontWeight: '700',
    color: '#14201A',
    marginBottom: 12,
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
    marginBottom: 10,
  },
  tagOrden: {
    backgroundColor: '#E2E8F0',
    borderRadius: 12,
    paddingHorizontal: 8,
    paddingVertical: 2,
    marginRight: 8,
  },
  tagOrdenText: {
    fontSize: 12,
    fontWeight: '700',
    color: '#334155',
  },
  parcelaId: {
    fontSize: 16,
    fontWeight: '700',
    color: '#1E293B',
    flex: 1,
  },
  tagEstado: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 6,
  },
  tagOk: {
    backgroundColor: '#D1E7DD',
  },
  tagRiesgo: {
    backgroundColor: '#F8D7DA',
  },
  tagEstadoTexto: {
    fontSize: 12,
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
    fontSize: 14,
    color: '#334155',
  },
  motivoAlerta: {
    fontSize: 12,
    color: '#A8452B',
    fontWeight: '600',
    marginTop: 4,
  },
  insumoNombre: {
    fontSize: 16,
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
    fontSize: 11,
    color: '#64748B',
    marginBottom: 2,
  },
  insumoColVal: {
    fontSize: 16,
    fontWeight: '700',
    color: '#1E293B',
  },
  deficitVal: {
    color: '#A8452B',
  },
  footer: {
    backgroundColor: '#FFFFFF',
    paddingVertical: 12,
    alignItems: 'center',
    borderTopWidth: 1,
    borderTopColor: '#E2E8F0',
  },
  footerTexto: {
    fontSize: 11,
    color: '#94A3B8',
  },
});
