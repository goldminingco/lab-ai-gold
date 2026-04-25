/** @type {import('next').NextConfig} */
const nextConfig = {
    reactStrictMode: true,
    typescript: { ignoreBuildErrors: true },
    eslint: { ignoreDuringBuilds: true },
    poweredByHeader: false,

    // Necessário para MapLibre GL funcionar no webpack
    webpack: (config, { isServer }) => {
          if (!isServer) {
                  config.resolve.alias = {
                            ...config.resolve.alias,
                            "mapbox-gl": "maplibre-gl",
                  };
          }
          // Evita erro com canvas no servidor
      config.resolve.fallback = {
        ...config.resolve.fallback,
              fs: false,
              net: false,
              tls: false,
      };
          return config;
    },

    async rewrites() {
          return [
            {
                      source: "/api/:path*",
                      destination: `${process.env.INTERNAL_API_URL ?? "http://api:8000"}/api/:path*`,
            },
                ];
    },

    async headers() {
          return [
            {
                      source: "/(.*)",
                      headers: [
                        { key: "X-Frame-Options", value: "DENY" },
                        { key: "X-Content-Type-Options", value: "nosniff" },
                        { key: "Strict-Transport-Security", value: "max-age=63072000; includeSubDomains; preload" },
                        { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
                        { key: "Permissions-Policy", value: "camera=(), microphone=(), geolocation=(self), interest-cohort=()" },
                        { key: "X-DNS-Prefetch-Control", value: "on" },
                        { key: "Cross-Origin-Opener-Policy", value: "same-origin" },
                                ],
            },
                ];
    },
};

export default nextConfig;
