--
--  Facam essa porra update safe plz
--

-- ***************************************************************
-- *********************** TABLES ********************************
-- ***************************************************************

create table if not exists c_run (
  run_id serial primary key,
  mode text,
  create_date timestamp default now(),
  update_date timestamp
);

create table if not exists c_cycle (
  cycle_id integer primary key,
  run_id integer references c_run (run_id),
  status text,
  symbol text,
  base_amount numeric default 0.0,
  profit numeric default 0.0,
  profit_perc numeric default 0.0,
  ref_date timestamp,                  -- hora que concluiu o ciclo
  create_date timestamp default now(),
  update_date timestamp
);

create table if not exists c_order (
  order_id integer,
  run_id integer references c_run (run_id),
  cycle_id integer references c_cycle (cycle_id),
  symbol text,
  type text,
  price numeric,
  amount numeric,
  avg_price numeric default 0.0,
  exec_amount numeric default 0.0,
  gross_total numeric default 0.0,
  net_total numeric default 0.0,
  fee_asset text,
  fee numeric default 0.0,
  simulation boolean,
  active boolean default true,
  ref_date timestamp,                    -- Hora que executou
  create_date timestamp default now(),
  update_date timestamp,
  PRIMARY KEY(order_id, run_id, cycle_id)
);

create table if not exists c_analysis (
  id serial primary key,
  run_id integer references  c_run (run_id),
  order_id integer,
  suggestion text,
  analysis text,
  price numeric,
  ref_date timestamp,
  create_date timestamp default now(),
  update_date timestamp
);

-- ***************************************************************
-- ********************* FUNCTIONS *******************************
-- ***************************************************************

CREATE OR REPLACE FUNCTION f_update_date()
RETURNS trigger AS $$
BEGIN
    NEW.update_date = now();
    return NEW;
END;
$$ language 'plpgsql';

-- ***************************************************************
-- ********************** TRIGGERS *******************************
-- ***************************************************************

DROP TRIGGER IF EXISTS t_update_run ON public.c_run;
CREATE TRIGGER t_update_run BEFORE UPDATE ON c_run FOR EACH ROW EXECUTE PROCEDURE f_update_date();

DROP TRIGGER IF EXISTS t_update_cycle ON public.c_cycle;
CREATE TRIGGER t_update_cycle BEFORE UPDATE ON c_cycle FOR EACH ROW EXECUTE PROCEDURE f_update_date();

DROP TRIGGER IF EXISTS t_update_order ON public.c_order;
CREATE TRIGGER t_update_order BEFORE UPDATE ON c_order FOR EACH ROW EXECUTE PROCEDURE f_update_date();

DROP TRIGGER IF EXISTS t_update_analysis on public.c_analysis;
CREATE TRIGGER t_update_analysis BEFORE UPDATE ON c_analysis FOR EACH ROW EXECUTE PROCEDURE f_update_date();


-- ***************************************************************
-- ********************** SEQUENCES ******************************
-- ***************************************************************

CREATE SEQUENCE IF NOT EXISTS s_fake_order_id START 1;
CREATE SEQUENCE IF NOT EXISTS s_cycle_id START 1;


-- ***************************************************************
-- ********************** VIEWS **********************************
-- ***************************************************************
