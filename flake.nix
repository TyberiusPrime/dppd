{
  description = "Wraps mbf-bam into an mach-nix importable builder";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/23.11";
  };

  outputs = {
    self,
    nixpkgs,
  }: let
    system = "x86_64-linux";
    overlays = [];
    pkgs = import nixpkgs {inherit system overlays;};
  in let
    palettable = let
      p = pkgs.python39Packages;
    in
      p.buildPythonPackage rec {
        pname = "palettable";
        version = "3.3.0";
        # buildInputs = [p.pandas];
        propagatedBuildInputs = [p.numpy p.setuptools];
        src = p.fetchPypi {
          inherit pname version;
          sha256 = "sha256-cv7Kcc99eYMM1tkYGwLt8ie4Z9UDvslTz5+pG/RIlr0=";
        };
      };

    mizani = let
      p = pkgs.python39Packages;
    in
      p.buildPythonPackage rec {
        pname = "mizani";
        version = "0.8.1";
        # buildInputs = [p.pandas];
        propagatedBuildInputs = [p.numpy palettable p.pandas p.matplotlib p.scipy];
        src = p.fetchPypi {
          inherit pname version;
          sha256 = "sha256-itCg76UvG830H2dbZKjA980k52PVO6ztZhPyC9btSSg=";
        };
        patchPhase = ''
          sed -i '3 a version=${version}' setup.cfg
        '';

        doCheck = false;
      };
    plotnine = let
      p = pkgs.python39Packages;
    in
      p.buildPythonPackage rec {
        pname = "plotnine";
        version = "0.10.1";
        buildInputs = [mizani];
        propagatedBuildInputs = [p.pandas p.statsmodels mizani];
        src = p.fetchPypi {
          inherit pname version;
          sha256 = "sha256-2RKgS2ONz4IsUaZ4i4VmQjI0jVFfFR2zpkwAAZZvaEE=";
        };
        doCheck = false;
      };

    mypython = pkgs.python39.withPackages (p: [
      #todo: figure out how to derive this from pyproject.toml
      p.pytest
      p.pytest-mock
      p.pytest-cov
      p.wrapt
      p.pandas
      p.numpy
      p.natsort
      plotnine
    ]);
  in {
    # pass in nixpkgs, mach-nix and what you want it to report back as a version
    devShell.x86_64-linux = pkgs.mkShell {
      # supplx the specific rust version
      # be sure to set this back in your build scripts,
      # otherwise pyo3 will get recompiled all the time
      nativeBuildInputs = [
        mypython
      ];
    };
  };
}
