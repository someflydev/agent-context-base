#[derive(Debug, Clone, Copy)]
pub struct Profile {
    pub num_orgs: usize,
    pub num_users: usize,
    pub seed: u64,
    pub name: &'static str,
}

impl Profile {
    pub const SMOKE: Profile = Profile {
        num_orgs: 3,
        num_users: 10,
        seed: 42,
        name: "smoke",
    };
    pub const SMALL: Profile = Profile {
        num_orgs: 20,
        num_users: 200,
        seed: 1000,
        name: "small",
    };
    pub const MEDIUM: Profile = Profile {
        num_orgs: 200,
        num_users: 5000,
        seed: 5000,
        name: "medium",
    };
    pub const LARGE: Profile = Profile {
        num_orgs: 2000,
        num_users: 50000,
        seed: 9999,
        name: "large",
    };

    pub fn resolve(name: &str, seed_override: Option<u64>) -> Profile {
        let mut profile = match name {
            "small" => Profile::SMALL,
            "medium" => Profile::MEDIUM,
            "large" => Profile::LARGE,
            _ => Profile::SMOKE,
        };
        if let Some(seed) = seed_override {
            profile.seed = seed;
        }
        profile
    }
}
