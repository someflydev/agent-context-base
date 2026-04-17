use serde::{Deserialize, Deserializer};

fn deserialize_vec<'de, D>(deserializer: D) -> Result<Vec<String>, D::Error>
where
    D: Deserializer<'de>,
{
    #[derive(Deserialize)]
    #[serde(untagged)]
    enum VecOrSingle {
        Vec(Vec<String>),
        Single(String),
    }

    Ok(match Option::<VecOrSingle>::deserialize(deserializer)? {
        Some(VecOrSingle::Vec(v)) => v,
        Some(VecOrSingle::Single(s)) if !s.is_empty() => vec![s],
        _ => vec![],
    })
}

#[derive(Debug, Default, Deserialize)]
pub struct FilterState {
    pub date_from: Option<String>,
    pub date_to: Option<String>,
    #[serde(default, deserialize_with = "deserialize_vec")]
    pub services: Vec<String>,
    #[serde(default, deserialize_with = "deserialize_vec")]
    pub severity: Vec<String>,
    #[serde(default, deserialize_with = "deserialize_vec")]
    pub environment: Vec<String>,
}