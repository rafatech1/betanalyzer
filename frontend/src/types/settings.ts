export interface AppSettings {
  banca_inicial: number;
  kelly_fraction: number;
  ev_threshold: number;
  favorite_league_ids: number[];
  updated_at: string;
}

export interface AppSettingsUpdate {
  banca_inicial?: number;
  kelly_fraction?: number;
  ev_threshold?: number;
  favorite_league_ids?: number[];
}
