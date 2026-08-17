-- Històric de dades del veïnat (format clau-valor amb marca de temps).
-- Cada fila és el valor d'un atribut d'una entitat en un instant concret.
-- Aquest disseny s'adapta a qualsevol entitat/atribut sense canviar l'esquema.

CREATE TABLE IF NOT EXISTS historic (
  id          BIGINT AUTO_INCREMENT PRIMARY KEY,
  ts          DATETIME     NOT NULL,           -- moment de la captura
  entitat     VARCHAR(128) NOT NULL,           -- id NGSI (ex: Bateria:Veinat:001)
  tipus       VARCHAR(64),                     -- type NGSI (ex: Llum, SensorAmbient)
  atribut     VARCHAR(64)  NOT NULL,           -- nom de l'atribut (ex: temperatura_c)
  valor_num   DOUBLE       NULL,               -- valor si és numèric o booleà (0/1)
  valor_text  VARCHAR(255) NULL,               -- valor si és text
  INDEX idx_entitat_ts (entitat, ts),
  INDEX idx_atribut_ts (atribut, ts),
  INDEX idx_tipus_ts   (tipus, ts)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
