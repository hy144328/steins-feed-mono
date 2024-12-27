import "./global.css"

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
<html lang="en">
  <head>
    <title>Stein&apos;s Feed</title>
  </head>
  <body>{children}</body>
</html>
  );
}
