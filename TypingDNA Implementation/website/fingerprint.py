import os
import cffi

ffi = cffi.FFI()

# Set the DLL directory
dll_directory = r"C:\Users\GanCY\Documents\APU(Y3S2)\Module\PROJECT\FreeFingerprintVerification_3_0_SDK\Bin\Win64_x64"
os.environ['PATH'] = dll_directory + os.pathsep + os.environ['PATH']

# Load the SDK library using the correct path
dll_path = os.path.join(dll_directory, "Nffv.dll")
if not os.path.isfile(dll_path):
    print(f"Error: The file {dll_path} does not exist.")
else:
    try:
        sdk_lib = ffi.dlopen(dll_path)

        # Define the C function signatures and types from the SDK.
        ffi.cdef("""
            typedef struct {
                unsigned char *data;
                int length;
            } Fingerprint;

            int InitializeFingerSDK();
            int CaptureFingerprint(Fingerprint *fingerprint);
            int EnrollFingerprint(Fingerprint *fingerprint);
            int VerifyFingerprint(Fingerprint *fingerprint);
            void CleanupFingerSDK();
        """)

        # Initialize the SDK
        if sdk_lib.InitializeFingerSDK() != 1:
            print("Failed to initialize the Finger SDK.")
            exit(1)

        # Create a fingerprint object
        fingerprint = ffi.new("Fingerprint *")

        # Capture fingerprint
        if sdk_lib.CaptureFingerprint(fingerprint) != 1:
            print("Failed to capture fingerprint.")
            exit(1)

        # Enroll the captured fingerprint
        if sdk_lib.EnrollFingerprint(fingerprint) != 1:
            print("Failed to enroll fingerprint.")
            exit(1)

        # Capture fingerprint for verification
        verification_fingerprint = ffi.new("Fingerprint *")
        if sdk_lib.CaptureFingerprint(verification_fingerprint) != 1:
            print("Failed to capture verification fingerprint.")
            exit(1)

        # Verify the fingerprint
        match = sdk_lib.VerifyFingerprint(verification_fingerprint)
        if match == 1:
            print("Fingerprints match!")
        else:
            print("Fingerprints do not match.")

        # Cleanup
        sdk_lib.CleanupFingerSDK()

    except OSError as e:
        print(f"Error: {e}")
