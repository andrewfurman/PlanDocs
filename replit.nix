{pkgs}: {
  deps = [
    pkgs.python311Packages.alembic
    pkgs.postgresql
  ];
}
