const Mongoose = require('mongoose');

const schema = new Mongoose.Schema({
  user_id: Number,
}, {
  timestamps: false,
});

module.exports = {
  collectionName: 'admins',
  modelName: 'admins',
  schema,
};
