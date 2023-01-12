DELETE from academicos_horario CASCADE;
DELETE from academicos_docente CASCADE;
DELETE from academicos_matricula CASCADE;
DELETE from economicos_pago CASCADE;
DELETE from admision_expediente CASCADE;
delete from core_persona CASCADE;



ALTER SEQUENCE core_persona_id_seq RESTART WITH 1;
UPDATE core_persona SET id = DEFAULT;

ALTER SEQUENCE admision_expediente_id_seq RESTART WITH 1;
UPDATE admision_expediente SET id = DEFAULT;

ALTER SEQUENCE economicos_pago_id_seq RESTART WITH 1;
UPDATE economicos_pago SET id = DEFAULT;

ALTER SEQUENCE academicos_matricula_id_seq RESTART WITH 1;
UPDATE academicos_matricula SET id = DEFAULT;

ALTER SEQUENCE academicos_docente_id_seq RESTART WITH 1;
UPDATE academicos_docente SET id = DEFAULT;

ALTER SEQUENCE academicos_horario_id_seq RESTART WITH 1;
UPDATE academicos_horario SET id = DEFAULT;
