export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
<html lang="en">
  <head>
    <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet"/>
    <title>Stein&apos;s Feed</title>
  </head>
  <body>{children}</body>
</html>
  );
}
