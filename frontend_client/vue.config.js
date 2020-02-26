const webpack = require('webpack');
//var path = require('path');

module.exports = {
  filenameHashing: false,
  chainWebpack: (config) => {
    config.resolve.symlinks(false)
  },
  configureWebpack: {
    devServer: {
      clientLogLevel: 'info',
      host: 'localhost',
      watchOptions: {
        ignored: ['node_modules'],
        poll: true
      },
    },
    plugins: [
      new webpack.ProvidePlugin({
        $: 'jquery',
        jquery: 'jquery',
        'window.jQuery': 'jquery',
        jQuery: 'jquery'
      })
    ]
  },

  publicPath: '',
}