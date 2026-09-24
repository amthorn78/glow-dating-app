const path = require('node:path');
const { getDefaultConfig } = require('expo/metro-config');

const config = getDefaultConfig(__dirname);
// Separate locked installs do not enable Expo's npm-workspace auto-detection.
// Watch only the canonical synthetic fixtures outside the mobile project root.
config.watchFolders = [...config.watchFolders, path.resolve(__dirname, '../../packages/contracts/fixtures')];
module.exports = config;
