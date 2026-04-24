% Copyright 2026 The MathWorks, Inc.
% These tests are designed to run INSIDE the docker container

classdef StartupSettingsTest < matlab.unittest.TestCase
    % StartupSettingsTest verifies that MATLAB has been configured
    % with the correct user preferences in matlabrc.m to suppress
    % unnecessary UI elements and warnings.
    methods(Test)
        function testGettingStartedIsDisabled(testCase)
            % Verify that the "Getting Started" window is suppressed
            s = settings;
            actualValue = s.matlab.commandwindow.GettingStarted.PersonalValue;
            testCase.verifyEqual(actualValue, false, ...
                "The 'Getting Started' window should be disabled in matlabrc.m.");
        end

        function testWarnIfRootIsDisabled(testCase)
            % Verify that the "Run as Root" warning is suppressed
            s = settings;
            actualValue = s.matlab.commandwindow.WarnIfRoot.PersonalValue;
            testCase.verifyEqual(actualValue, false, ...
                "The 'Warn if Root' message should be disabled in matlabrc.m.");
        end
    end
end
