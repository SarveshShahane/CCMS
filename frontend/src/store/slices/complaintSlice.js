import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { complaintApi } from '../../api/api';

const initialFormState = {
  customer_name: '',
  complaint_source: 'Pharmacy',
  customer_contact_email: '',
  customer_contact_phone: '',
  product_name: '',
  product_code: '',
  dosage_form: 'Capsules',
  product_strength: '',
  batch_number: '',
  affected_quantity: 1,
  affected_quantity_unit: 'units',
  complaint_category: 'Packaging / Labeling',
  title: '',
  description: '',
  initial_severity: 'Major',
  ai_risk_assessment: '',
  ai_suggested_next_action: '',
  incident_date: '',
  manufacturing_date: '',
  expiry_date: '',
  sample_received: false,
};

// Save complaint payload to database
export const saveComplaintThunk = createAsyncThunk(
  'complaint/saveComplaint',
  async (_, { getState, rejectWithValue }) => {
    try {
      const { complaint } = getState();
      const payload = {
        ...complaint.form,
        affected_quantity: parseFloat(complaint.form.affected_quantity) || 1,
        incident_date: complaint.form.incident_date || null,
        manufacturing_date: complaint.form.manufacturing_date || null,
        expiry_date: complaint.form.expiry_date || null,
      };

      const response = await complaintApi.saveComplaint(payload);
      return response;
    } catch (err) {
      return rejectWithValue(err.message || 'Failed to save complaint');
    }
  }
);

export const complaintSlice = createSlice({
  name: 'complaint',
  initialState: {
    form: { ...initialFormState },
    autoFilledFields: [],
    isSaving: false,
    saveSuccess: false,
    saveError: null,
    lastSavedNumber: null,
  },
  reducers: {
    updateFormField: (state, action) => {
      const { field, value } = action.payload;
      state.form[field] = value;
      // Remove field from autoFilled highlight if user manually edits it
      state.autoFilledFields = state.autoFilledFields.filter((f) => f !== field);
    },
    autoFillFromAI: (state, action) => {
      const extracted = action.payload;
      if (!extracted) return;

      const updatedKeys = [];
      const mappingKeys = [
        'customer_name',
        'customer_contact_email',
        'customer_contact_phone',
        'complaint_source',
        'product_name',
        'product_code',
        'dosage_form',
        'product_strength',
        'batch_number',
        'affected_quantity',
        'affected_quantity_unit',
        'complaint_category',
        'title',
        'description',
        'initial_severity',
        'ai_risk_assessment',
        'ai_suggested_next_action',
        'manufacturing_date',
        'expiry_date',
        'incident_date',
      ];

      mappingKeys.forEach((key) => {
        if (extracted[key] !== undefined && extracted[key] !== null && extracted[key] !== '') {
          state.form[key] = extracted[key];
          updatedKeys.push(key);
        }
      });

      state.autoFilledFields = updatedKeys;
    },
    clearForm: (state) => {
      state.form = { ...initialFormState };
      state.autoFilledFields = [];
      state.saveSuccess = false;
      state.saveError = null;
    },
    resetSaveStatus: (state) => {
      state.saveSuccess = false;
      state.saveError = null;
      state.lastSavedNumber = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(saveComplaintThunk.pending, (state) => {
        state.isSaving = true;
        state.saveError = null;
        state.saveSuccess = false;
      })
      .addCase(saveComplaintThunk.fulfilled, (state, action) => {
        state.isSaving = false;
        state.saveSuccess = true;
        state.lastSavedNumber = action.payload.complaint_number;
        // Form clears upon successful save as required
        state.form = { ...initialFormState };
        state.autoFilledFields = [];
      })
      .addCase(saveComplaintThunk.rejected, (state, action) => {
        state.isSaving = false;
        state.saveError = action.payload || 'Error saving complaint';
        state.saveSuccess = false;
      });
  },
});

export const { updateFormField, autoFillFromAI, clearForm, resetSaveStatus } = complaintSlice.actions;
export default complaintSlice.reducer;
