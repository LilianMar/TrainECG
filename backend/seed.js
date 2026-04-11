/**
 * seed.js — TrainECG Database Seed
 *
 * Inserta datos iniciales en la base de datos SQLite:
 *   - 20 preguntas de práctica (practice_questions)
 *   - Usuario administrador/demo
 *
 * Uso:
 *   bun seed.js                          # ruta por defecto: ./ecg_app.db
 *   bun seed.js --db /ruta/a/ecg_app.db  # ruta personalizada
 *
 * Requisitos:
 *   - Bun >= 1.0  (usa bun:sqlite nativo, sin dependencias externas)
 *   - La base de datos debe existir y tener las tablas creadas.
 *     Si el contenedor ya está arriba, las tablas existen automáticamente
 *     (SQLAlchemy las crea al iniciar el backend).
 *
 * Después de correr el seed, reiniciar el backend es opcional:
 *   docker compose restart backend
 */

import { Database } from "bun:sqlite";
import { resolve } from "path";

// ─── Ruta a la base de datos ───────────────────────────────────────────────
const dbArg = process.argv.indexOf("--db");
const DB_PATH =
  dbArg !== -1
    ? resolve(process.argv[dbArg + 1])
    : resolve(import.meta.dir, "db", "ecg_app.db");

console.log(`\n🌱 TrainECG Seed`);
console.log(`   DB: ${DB_PATH}\n`);

const db = new Database(DB_PATH);
db.exec("PRAGMA journal_mode=WAL;");

// ─── Datos: preguntas de práctica ──────────────────────────────────────────
const PRACTICE_QUESTIONS = [
  {
    id: 1,
    image_filename: "ecg_case_1.png",
    image_path: "/uploads/practice_ecgs/ecg_case_1.png",
    question_text:
      "¿Cuál es la arritmia más probable evidenciada en este electrocardiograma?",
    option_a:
      "Taquicardia sinusal con extrasístoles auriculares frecuentes",
    option_b:
      "Fibrilación auricular con respuesta ventricular rápida",
    option_c: "Flutter auricular con bloqueo AV variable",
    option_d: "Taquicardia ventricular monomórfica",
    correct_answer: 1,
    explanation:
      "El ECG muestra intervalos R-R completamente irregulares, ausencia de ondas P bien definidas y una línea basal con oscilaciones irregulares de baja amplitud (ondas fibrilatorias 'f'), hallazgos patognomónicos de fibrilación auricular (FA).",
    correct_class: "atrial_fibrillation",
    difficulty_level: 2,
  },
  {
    id: 2,
    image_filename: "ecg_case_1.png",
    image_path: "/uploads/practice_ecgs/ecg_case_1.png",
    question_text:
      "¿Cuál de las siguientes características electrocardiográficas es la MÁS específica de esta arritmia?",
    option_a: "Complejos QRS anchos (>120 ms)",
    option_b: "Intervalos PR prolongados",
    option_c:
      "Ausencia de ondas P con línea basal fibrilatoria (ondas 'f')",
    option_d: "Ondas P negativas en derivaciones inferiores",
    correct_answer: 2,
    explanation:
      "La ausencia de ondas P discretas reemplazadas por una línea de base fibrilatoria (ondas 'f' a 350-600 lpm) con intervalos R-R irregulares es el sello diagnóstico de la fibrilación auricular.",
    correct_class: "atrial_fibrillation",
    difficulty_level: 3,
  },
  {
    id: 3,
    image_filename: "ecg_case_2.png",
    image_path: "/uploads/practice_ecgs/ecg_case_2.png",
    question_text: "¿Cuál es el diagnóstico electrocardiográfico más probable?",
    option_a:
      "Taquicardia supraventricular con aberrancia de conducción",
    option_b: "Fibrilación ventricular",
    option_c: "Taquicardia ventricular monomórfica sostenida",
    option_d:
      "Bloqueo de rama derecha con taquicardia sinusal",
    correct_answer: 2,
    explanation:
      "El ECG muestra taquicardia regular a ~180 lpm con complejos QRS anchos (>120 ms) de morfología bizarra, sin ondas P identificables antes de cada QRS. En el contexto de cardiopatía isquémica previa e inestabilidad hemodinámica, el diagnóstico es taquicardia ventricular (TV) monomórfica sostenida hasta demostrar lo contrario.",
    correct_class: "ventricular_tachycardia",
    difficulty_level: 3,
  },
  {
    id: 4,
    image_filename: "ecg_case_2.png",
    image_path: "/uploads/practice_ecgs/ecg_case_2.png",
    question_text:
      "Según el criterio de Brugada, ¿cuál hallazgo favorece el origen ventricular sobre supraventricular?",
    option_a: "Duración del QRS < 140 ms",
    option_b:
      "Intervalo RS > 100 ms en derivaciones precordiales",
    option_c: "Eje eléctrico normal (0° a +90°)",
    option_d: "Presencia de ondas P antes de cada QRS",
    correct_answer: 1,
    explanation:
      "Dentro del algoritmo de Brugada, un intervalo RS >100 ms en cualquier derivación precordial es altamente sugestivo de taquicardia ventricular. La disociación AV, la captura y los latidos de fusión son los criterios más específicos, pero el RS prolongado es el primer paso del algoritmo.",
    correct_class: "ventricular_tachycardia",
    difficulty_level: 4,
  },
  {
    id: 5,
    image_filename: "ecg_case_3.png",
    image_path: "/uploads/practice_ecgs/ecg_case_3.png",
    question_text:
      "¿Cuál es la arritmia que mejor describe este electrocardiograma?",
    option_a: "Bloqueo AV de primer grado",
    option_b: "Bloqueo AV de segundo grado tipo Mobitz II",
    option_c: "Bloqueo AV completo (tercer grado)",
    option_d: "Síndrome de seno enfermo",
    correct_answer: 2,
    explanation:
      "El patrón de ondas P que ocurren a una frecuencia regular (~80 lpm) y complejos QRS anchos lentos a otra frecuencia independiente (~35 lpm), sin relación entre sí (disociación AV completa), es diagnóstico de bloqueo AV de tercer grado o completo. El ritmo de escape es ventricular (ancho) indicando bloqueo infra-Hisiano.",
    correct_class: "av_block",
    difficulty_level: 3,
  },
  {
    id: 6,
    image_filename: "ecg_case_3.png",
    image_path: "/uploads/practice_ecgs/ecg_case_3.png",
    question_text:
      "¿Cuál es el tratamiento de primera línea definitivo para este paciente?",
    option_a: "Amiodarona intravenosa",
    option_b:
      "Marcapasos transcutáneo como puente, seguido de marcapasos definitivo",
    option_c: "Cardioversión eléctrica sincronizada",
    option_d: "Digoxina para aumentar la conducción AV",
    correct_answer: 1,
    explanation:
      "El bloqueo AV completo sintomático (síncope, bradicardia severa) requiere marcapasos transcutáneo o transvenoso de urgencia como puente, seguido de implante de marcapasos definitivo bicameral. La digoxina está contraindicada pues empeora el bloqueo AV.",
    correct_class: "av_block",
    difficulty_level: 3,
  },
  {
    id: 7,
    image_filename: "ecg_case_4.png",
    image_path: "/uploads/practice_ecgs/ecg_case_4.png",
    question_text:
      "¿Cuál de las siguientes arritmias corresponde al patrón de 'dientes de sierra' (ondas F) a 300 lpm en la línea basal?",
    option_a: "Fibrilación auricular",
    option_b: "Flutter auricular típico con bloqueo AV 4:1",
    option_c: "Taquicardia auricular multifocal",
    option_d: "Taquicardia sinusal inapropiada",
    correct_answer: 1,
    explanation:
      "El flutter auricular típico (istmo cavotricuspídeo) produce ondas F en dientes de sierra a ~300 lpm, mejor vistas en DII, DIII y aVF. Con bloqueo AV 4:1, la frecuencia ventricular resultante es ~75 lpm. La morfología negativa en cara inferior de las ondas F confirma el flutter típico antihorario.",
    correct_class: "atrial_flutter",
    difficulty_level: 2,
  },
  {
    id: 8,
    image_filename: "ecg_case_4.png",
    image_path: "/uploads/practice_ecgs/ecg_case_4.png",
    question_text:
      "¿En qué derivaciones son mejor visibles las ondas F del flutter auricular típico?",
    option_a: "V1 y V2",
    option_b: "aVR y aVL",
    option_c: "DII, DIII y aVF",
    option_d: "V4, V5 y V6",
    correct_answer: 2,
    explanation:
      "En el flutter típico (macrorreentrante antihorario en el istmo cavotricuspídeo), las ondas F se observan con mayor claridad en las derivaciones inferiores (DII, DIII, aVF) como deflexiones negativas en dientes de sierra, y en V1 como ondas positivas discretas.",
    correct_class: "atrial_flutter",
    difficulty_level: 3,
  },
  {
    id: 9,
    image_filename: "ecg_case_5.png",
    image_path: "/uploads/practice_ecgs/ecg_case_5.png",
    question_text:
      "¿Cuál es el diagnóstico más probable para esta taquicardia regular de QRS estrecho a 175 lpm en paciente joven sin cardiopatía?",
    option_a: "Taquicardia ventricular monomórfica",
    option_b: "Fibrilación auricular con respuesta rápida",
    option_c:
      "Taquicardia por reentrada nodal AV (TRNAV) o taquicardia supraventricular paroxística",
    option_d: "Taquicardia sinusal por ansiedad",
    correct_answer: 2,
    explanation:
      "La taquicardia supraventricular paroxística (TPSV) —más frecuentemente por reentrada nodal AV (TRNAV)— se presenta clásicamente en adultos jóvenes sin cardiopatía con episodios de palpitaciones de inicio y fin bruscos, FC 150-250 lpm, QRS estrecho y respuesta a maniobras vagales/adenosina.",
    correct_class: "svt_paroxysmal",
    difficulty_level: 2,
  },
  {
    id: 10,
    image_filename: "ecg_case_5.png",
    image_path: "/uploads/practice_ecgs/ecg_case_5.png",
    question_text:
      "¿Cuál es el fármaco de elección para terminar de forma aguda un episodio de taquicardia supraventricular paroxística refractaria a maniobras vagales?",
    option_a: "Amiodarona 150 mg IV",
    option_b: "Adenosina 6 mg IV en bolo rápido",
    option_c: "Metoprolol 50 mg VO",
    option_d: "Digoxina 0.25 mg IV",
    correct_answer: 1,
    explanation:
      "La adenosina es el fármaco de primera línea para la TSV paroxística aguda. Su mecanismo de bloqueo transitorio del nodo AV interrumpe el circuito reentrante. Se administra en bolo IV rápido (6 mg; si no revierte, 12 mg repetidos hasta 3 dosis) seguido de flush de suero salino. Tiene vida media de 10-15 segundos.",
    correct_class: "svt_paroxysmal",
    difficulty_level: 3,
  },
  {
    id: 11,
    image_filename: "ecg_img_1.png",
    image_path: "/uploads/practice_ecgs/ecg_img_1.png",
    question_text:
      "¿Cómo interpreta esta tira de ritmo ECG auricular?",
    option_a: "Fibrilación auricular",
    option_b: "Flutter auricular",
    option_c: "Taquicardia auricular multifocal",
    option_d:
      "Marcapasos auricular errante (Wandering Atrial Pacemaker)",
    correct_answer: 3,
    explanation:
      "El marcapasos auricular errante se caracteriza por ondas P con morfología cambiante en una misma derivación (al menos 3 morfologías distintas), intervalos PR variables y frecuencia cardiaca normal o ligeramente disminuida. El marcapasos se desplaza entre el nodo SA y focos auriculares ectópicos.",
    correct_class: "wandering_atrial_pacemaker",
    difficulty_level: 3,
  },
  {
    id: 12,
    image_filename: "ecg_img_2.png",
    image_path: "/uploads/practice_ecgs/ecg_img_2.png",
    question_text:
      "En esta tira de ECG, la variación en la morfología de las ondas P sugiere que el marcapasos cardíaco se origina en:",
    option_a: "El haz de His únicamente",
    option_b: "Un único foco ectópico ventricular",
    option_c:
      "Múltiples focos auriculares (nodo SA y focos ectópicos auriculares)",
    option_d: "El nodo AV de forma fija",
    correct_answer: 2,
    explanation:
      "En el marcapasos auricular errante, el impulso cardíaco se origina alternativamente en el nodo sinusal y en diferentes focos ectópicos auriculares, lo que produce variación en la morfología de las ondas P, cambios en el intervalo PR y ritmo ligeramente irregular.",
    correct_class: "wandering_atrial_pacemaker",
    difficulty_level: 3,
  },
  {
    id: 13,
    image_filename: "ecg_img_3.png",
    image_path: "/uploads/practice_ecgs/ecg_img_3.png",
    question_text:
      "En esta tira de ECG auricular, la aparición de un latido adelantado con onda P de morfología diferente a los demás es característico de:",
    option_a: "Flutter auricular",
    option_b: "Fibrilación auricular",
    option_c: "Complejo auricular prematuro (CAP)",
    option_d: "Taquicardia supraventricular paroxística",
    correct_answer: 2,
    explanation:
      "El complejo auricular prematuro (CAP) o extrasístole auricular se manifiesta como un latido precoz con onda P de morfología diferente a la sinusal (P' ectópica), seguido de un complejo QRS estrecho normal y una pausa compensadora incompleta. El PR puede ser normal o diferente según la localización del foco.",
    correct_class: "premature_atrial_complex",
    difficulty_level: 2,
  },
  {
    id: 14,
    image_filename: "ecg_img_4.png",
    image_path: "/uploads/practice_ecgs/ecg_img_4.png",
    question_text:
      "Analice esta tira de ritmo. ¿Cuál de las siguientes arritmias auriculares se evidencia?",
    option_a: "Taquicardia auricular multifocal",
    option_b: "Bigeminismo auricular",
    option_c: "Bloqueo AV de segundo grado tipo Wenckebach",
    option_d:
      "Marcapasos auricular errante (Wandering Atrial Pacemaker)",
    correct_answer: 3,
    explanation:
      "La presencia de al menos 3 morfologías distintas de onda P con frecuencia cardiaca normal (<100 lpm) diferencia el marcapasos auricular errante de la taquicardia auricular multifocal (que requiere FC >100 lpm). Los intervalos R-R son irregulares pero sin la desorganización total de la fibrilación auricular.",
    correct_class: "wandering_atrial_pacemaker",
    difficulty_level: 3,
  },
  {
    id: 15,
    image_filename: "ecg_img_5.png",
    image_path: "/uploads/practice_ecgs/ecg_img_5.png",
    question_text:
      "Esta tira de ECG ventricular muestra una actividad eléctrica completamente caótica sin complejos QRS definibles. ¿Cuál es el diagnóstico?",
    option_a: "Taquicardia ventricular monomórfica",
    option_b: "Torsades de Pointes",
    option_c: "Fibrilación ventricular",
    option_d: "Flutter ventricular",
    correct_answer: 2,
    explanation:
      "La fibrilación ventricular (FV) se caracteriza por una actividad eléctrica ventricular completamente desorganizada, sin complejos QRS distinguibles, con ondas de amplitud y frecuencia irregulares (~200-450 lpm). Es una emergencia cardíaca que requiere desfibrilación inmediata ya que no hay gasto cardiaco efectivo.",
    correct_class: "ventricular_fibrillation",
    difficulty_level: 2,
  },
  {
    id: 16,
    image_filename: "ecg_img_6.png",
    image_path: "/uploads/practice_ecgs/ecg_img_6.png",
    question_text:
      "En esta tira de ECG ventricular se observa una línea casi isoeléctrica sin actividad eléctrica identificable. ¿Cuál es el diagnóstico correcto?",
    option_a: "Ritmo idioventricular acelerado",
    option_b: "Bloqueo AV completo con escape ventricular",
    option_c: "Fibrilación ventricular de baja amplitud",
    option_d: "Asistolia",
    correct_answer: 3,
    explanation:
      "La asistolia es la ausencia total de actividad eléctrica cardíaca, representada por una línea isoeléctrica en el ECG. Es uno de los ritmos de paro cardíaco no desfibrilable. El tratamiento incluye RCP de alta calidad y adrenalina IV cada 3-5 minutos, junto con identificación y tratamiento de causas reversibles (4H/4T).",
    correct_class: "asystole",
    difficulty_level: 2,
  },
  {
    id: 17,
    image_filename: "ecg_img_7.png",
    image_path: "/uploads/practice_ecgs/ecg_img_7.png",
    question_text:
      "En esta tira de ECG ventricular se observan complejos QRS anchos y bizarros que aparecen cada 4 latidos (uno ectópico por cada 3 sinusales). ¿Cómo se denomina este patrón?",
    option_a: "Complejo ventricular prematuro: bigeminismo",
    option_b: "Complejo ventricular prematuro: trigeminismo",
    option_c: "Complejo ventricular prematuro: cuadrigeminismo",
    option_d: "Ritmo idioventricular acelerado",
    correct_answer: 2,
    explanation:
      "El cuadrigeminismo ventricular es un patrón donde cada cuarto latido es un complejo ventricular prematuro (CVP), es decir, 3 latidos sinusales seguidos de 1 CVP de forma repetitiva. El CVP se caracteriza por QRS ancho (>120 ms), morfología bizarra, ausencia de onda P precedente y onda T de polaridad opuesta al QRS.",
    correct_class: "pvc_quadrigeminy",
    difficulty_level: 3,
  },
  {
    id: 18,
    image_filename: "ecg_img_8.png",
    image_path: "/uploads/practice_ecgs/ecg_img_8.png",
    question_text:
      "Esta tira de ECG ventricular muestra una taquicardia con complejos QRS que cambian de amplitud y eje, creando un patrón sinusoidal que 'gira' alrededor de la línea isoeléctrica. ¿Cuál es el diagnóstico?",
    option_a: "Flutter ventricular",
    option_b: "Fibrilación ventricular",
    option_c: "Taquicardia ventricular monomórfica",
    option_d: "Taquicardia ventricular Torsades de Pointes",
    correct_answer: 3,
    explanation:
      "Torsades de Pointes (TdP) es una taquicardia ventricular polimórfica caracterizada por complejos QRS que cambian progresivamente de amplitud y eje, girando en torno a la línea basal. Se asocia a QT largo (congénito o adquirido por fármacos, electrolitos). El tratamiento incluye sulfato de magnesio IV y corrección de la causa subyacente.",
    correct_class: "torsade_de_pointes",
    difficulty_level: 4,
  },
  {
    id: 19,
    image_filename: "ecg_img_9.png",
    image_path: "/uploads/practice_ecgs/ecg_img_9.png",
    question_text:
      "Esta tira de ECG de origen sinusal muestra un ritmo regular con ondas P positivas en DII antes de cada QRS y frecuencia cardiaca >100 lpm. ¿Cuál es el diagnóstico?",
    option_a: "Ritmo sinusal normal",
    option_b: "Arritmia sinusal",
    option_c: "Taquicardia sinusal",
    option_d: "Paro sinusal",
    correct_answer: 2,
    explanation:
      "La taquicardia sinusal se define como un ritmo de origen sinusal (onda P positiva en DII con PR normal) con frecuencia cardiaca >100 lpm. Es generalmente secundaria a causas fisiológicas o patológicas (fiebre, deshidratación, anemia, ansiedad, hipertiroidismo, entre otras) y rara vez requiere tratamiento específico más allá de la causa subyacente.",
    correct_class: "sinus_tachycardia",
    difficulty_level: 1,
  },
  {
    id: 20,
    image_filename: "ecg_img_10.png",
    image_path: "/uploads/practice_ecgs/ecg_img_10.png",
    question_text:
      "Esta tira de ECG de origen sinusal muestra un ritmo regular con ondas P sinusales y frecuencia cardiaca <60 lpm. ¿Cuál es el diagnóstico?",
    option_a: "Ritmo sinusal normal",
    option_b: "Arritmia sinusal",
    option_c: "Bradicardia sinusal",
    option_d: "Bloqueo AV de primer grado",
    correct_answer: 2,
    explanation:
      "La bradicardia sinusal se caracteriza por un ritmo regular de origen sinusal (ondas P positivas en DII con morfología normal, PR constante) con frecuencia cardiaca <60 lpm. Puede ser fisiológica (deportistas, sueño, tono vagal elevado) o patológica (hipotiroidismo, fármacos como betabloqueantes, síndrome del seno enfermo). Solo requiere tratamiento si es sintomática (atropina, marcapasos).",
    correct_class: "sinus_bradycardia",
    difficulty_level: 1,
  },
];

// ─── Datos: usuario administrador/demo ────────────────────────────────────
// Contraseña hasheada con bcrypt (hash del password original).
// Si se necesita cambiar la contraseña, generar nuevo hash con:
//   python3 -c "from passlib.hash import bcrypt; print(bcrypt.hash('nueva_password'))"
const ADMIN_USER = {
  name: "lilian maradiago",
  email: "lilian.maradiago@gmail.com",
  hashed_password:
    "$2b$12$iF.IvwJRQmd.BD4I3gDzh.pP6GxX4.Zbf7Dvhn7K5jMxVVCx4b01C",
  user_type: "STUDENT",
  institution: "USB",
  skill_level: 3,
  initial_test_completed: 1,
  initial_test_score: 2,
};

// ─── Seed: practice_questions ─────────────────────────────────────────────
function seedQuestions() {
  const insertQ = db.prepare(`
    INSERT OR IGNORE INTO practice_questions
      (id, image_filename, image_path, question_text,
       option_a, option_b, option_c, option_d,
       correct_answer, explanation, correct_class, difficulty_level)
    VALUES
      ($id, $image_filename, $image_path, $question_text,
       $option_a, $option_b, $option_c, $option_d,
       $correct_answer, $explanation, $correct_class, $difficulty_level)
  `);

  let inserted = 0;
  const tx = db.transaction(() => {
    for (const q of PRACTICE_QUESTIONS) {
      const result = insertQ.run({
        $id: q.id,
        $image_filename: q.image_filename,
        $image_path: q.image_path,
        $question_text: q.question_text,
        $option_a: q.option_a,
        $option_b: q.option_b,
        $option_c: q.option_c,
        $option_d: q.option_d,
        $correct_answer: q.correct_answer,
        $explanation: q.explanation,
        $correct_class: q.correct_class,
        $difficulty_level: q.difficulty_level,
      });
      if (result.changes > 0) inserted++;
    }
  });
  tx();

  const total = db
    .prepare("SELECT COUNT(*) as n FROM practice_questions")
    .get().n;
  console.log(
    `   practice_questions: ${inserted} insertadas, ${total} total en DB`
  );
}

// ─── Seed: usuario admin ──────────────────────────────────────────────────
function seedAdminUser() {
  const exists = db
    .prepare("SELECT id FROM users WHERE email = $email")
    .get({ $email: ADMIN_USER.email });

  if (exists) {
    console.log(`   users: ya existe "${ADMIN_USER.email}" (id=${exists.id}), sin cambios`);
    return;
  }

  db.prepare(`
    INSERT INTO users
      (name, email, hashed_password, user_type, institution,
       skill_level, initial_test_completed, initial_test_score,
       is_active, is_verified)
    VALUES
      ($name, $email, $hashed_password, $user_type, $institution,
       $skill_level, $initial_test_completed, $initial_test_score,
       1, 0)
  `).run({
    $name: ADMIN_USER.name,
    $email: ADMIN_USER.email,
    $hashed_password: ADMIN_USER.hashed_password,
    $user_type: ADMIN_USER.user_type,
    $institution: ADMIN_USER.institution,
    $skill_level: ADMIN_USER.skill_level,
    $initial_test_completed: ADMIN_USER.initial_test_completed,
    $initial_test_score: ADMIN_USER.initial_test_score,
  });

  console.log(`   users: usuario "${ADMIN_USER.email}" creado`);
}

// ─── Main ─────────────────────────────────────────────────────────────────
try {
  seedQuestions();
  seedAdminUser();
  console.log("\n   Seed completado.\n");
} catch (err) {
  console.error("\n   Error durante el seed:", err.message);
  console.error(
    "   Asegúrate de que la base de datos existe y tiene las tablas creadas."
  );
  console.error(
    "   Levanta el backend primero: docker compose up -d backend\n"
  );
  process.exit(1);
} finally {
  db.close();
}
