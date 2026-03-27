% Copyright 2026 The MathWorks, Inc.
% These tests are designed to run INSIDE the docker container

classdef InstalledProductsTest < matlab.unittest.TestCase
    % InstalledProductsTest checks that Database toolbox
    % is available in the MATLAB Docker image distribution.
    methods(Test)
        function testDatabaseToolboxIsInstalled(testCase)
            installedAddons = matlab.addons.installedAddons();
            expectedToolboxName = "Database Toolbox";
            testCase.verifyTrue(any(ismember(installedAddons.Name, expectedToolboxName)), ...
                "The expected 'Database Toolbox' is not installed.");
        end % testDatabaseToolboxIsInstalled
    end % methods(Test)
end % classdef
