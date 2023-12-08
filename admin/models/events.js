const Mongoose = require('mongoose');

const schema = new Mongoose.Schema({
  date: Date,
  description: String,
  name: String,
  image_id: String,
}, {
  timestamps: false,
});

module.exports = {
  collectionName: 'events',
  modelName: 'events',
  schema,
};
