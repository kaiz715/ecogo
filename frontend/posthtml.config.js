const urlRegex = new RegExp('^(?:[a-z]+:)?//', 'i');

module.exports = {
  plugins: {
    "posthtml-include": {},
     "posthtml-shorten": {
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
    },
  }
}
