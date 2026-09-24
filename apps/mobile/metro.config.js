const path = require('node:path');
const { getDefaultConfig } = require('expo/metro-config');

const config = getDefaultConfig(__dirname);
// Separate locked installs do not enable Expo's npm-workspace auto-detection.
// Watch the canonical shared fixtures and transition oracle outside the mobile root.
// The production directory contains contract data; this enables no production API.
config.watchFolders = [...config.watchFolders,
  path.resolve(__dirname, '../../packages/contracts/fixtures'),
  path.resolve(__dirname, '../../packages/contracts/production'),
];
module.exports = config;
