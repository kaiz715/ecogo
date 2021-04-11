const webpack = require('webpack');
const path = require('path');
const glob = require("glob");

const urlRegex = new RegExp('^(?:[a-z]+:)?//', 'i');

const config = {
  entry: './src/index.html',
  output: {
    path: path.resolve(__dirname, 'dist'),
    publicPath: '/public',
    filename: '[name].html'
    //filename: 'bundle.js'
  },
  module: {
    rules: [
      {
        test: /\.(css)$/,
        use: ['style-loader', 'css-loader']
      },
        {
          test: /\.html$/,
          type: 'asset/resource',
          generator: {
            filename: '[name][ext]',
          },
        },
      //{
      //  test: /\.png$/,
      //  use: [
      //    {
      //      loader: 'url-loader',
      //      options: {
      //        mimetype: 'image/png'
      //      }
      //    }
      //  ]
      //},
      //{
      //  test: /\.svg$/,
      //  use: 'file-loader'
      //},
      {
        test: /src.*\.html$/i,
        use: ['file-loader',
          {
            loader: 'posthtml-loader',
            options: {
              ident: 'posthtml',
              plugins: [
                /* PostHTML Plugins */
             //   require('posthtml-include')(),
                     require('posthtml-shorten')({
                       shortener: {
                         process: function (url) {
                           return new Promise((resolve, reject) => {
                             if (urlRegex.test(url))
                               resolve(url);
                             else resolve(url.replace(".html", ""));
                           });
                         },
                       },
                       tag: ["a"], // Allowed tags for URL shortening
                       attribute: ["href"], // Attributes to replace on the elements
                     }),
              ]
            }
          },
          'raw-loader',
        ],
      },
      { test: /include.*html$/i, loader: 'html-loader', },


    ]
  }
};

module.exports = config;
