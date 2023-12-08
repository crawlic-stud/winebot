const Mongoose = require('mongoose');

const schema = new Mongoose.Schema({
  image_id: String,
  description: String,
  name: String,
  price: Number,
}, {
  timestamps: false,
});

module.exports = {
  collectionName: 'products',
  modelName: 'products',
  schema,
};
