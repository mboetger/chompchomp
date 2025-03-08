const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function(app) {
  app.use(
    '/api',
    createProxyMiddleware({
      target: 'http://localhost:9999',
      changeOrigin: true,
    })
  );
  app.use(
    '/admin',
    createProxyMiddleware({
      target: 'http://localhost:5555/admin/',
      changeOrigin: true,
    })
  );
};