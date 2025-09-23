// MongoDB initialization script
db = db.getSiblingDB('ugc_saas');

// Create collections with indexes
db.createCollection('users');
db.createCollection('profiles');
db.createCollection('metrics');
db.createCollection('reports');
db.createCollection('posts_feedback');

// Create indexes for better performance
print('Creating indexes...');

// Users indexes
db.users.createIndex({ "email": 1 }, { unique: true });
db.users.createIndex({ "is_active": 1 });
db.users.createIndex({ "created_at": 1 });

// Profiles indexes
db.profiles.createIndex({ "user_id": 1 }, { unique: true });
db.profiles.createIndex({ "niche": 1 });
db.profiles.createIndex({ "instagram_tokens.user_id": 1 });

// Metrics indexes
db.metrics.createIndex({ "profile_id": 1, "date": -1 });
db.metrics.createIndex({ "date": -1 });
db.metrics.createIndex({ "profile_id": 1 });

// Reports indexes
db.reports.createIndex({ "profile_id": 1, "created_at": -1 });
db.reports.createIndex({ "report_type": 1 });
db.reports.createIndex({ "is_ready": 1 });
db.reports.createIndex({ "created_at": -1 });

// Posts feedback indexes
db.posts_feedback.createIndex({ "profile_id": 1, "created_at": -1 });
db.posts_feedback.createIndex({ "post_id": 1 }, { unique: true });
db.posts_feedback.createIndex({ "created_at": -1 });
db.posts_feedback.createIndex({ "scores.overall": -1 });

print('Database initialization completed successfully!');
print('Collections created: users, profiles, metrics, reports, posts_feedback');
print('Indexes created for optimal performance');

// Create a sample admin user (optional)
/*
db.users.insertOne({
  "email": "admin@ugcsaas.com",
  "full_name": "Admin User",
  "hashed_password": "$2b$12$example_hashed_password",
  "is_active": true,
  "is_superuser": true,
  "created_at": new Date(),
  "updated_at": new Date()
});
*/

