{ lib, python3Packages }:

python3Packages.buildPythonApplication {
  pname = "zte-exporter";
  version = "0.1.0";

  src = ./.;

  propagatedBuildInputs = with python3Packages;
    [ requests prometheus-client ];
  doCheck = false;
}
